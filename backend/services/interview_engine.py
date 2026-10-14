import logging
from typing import Dict, Any, List, Optional
from backend.db.models import (
    InterviewSessionDAO,
    InterviewTurnDAO,
    JobAnalysisDAO,
    CandidateAnalysisDAO,
    JobFitDAO
)
from backend.services.llm_provider import get_llm_provider

logger = logging.getLogger(__name__)


class InterviewEngine:
    @staticmethod
    async def start_session(
        job_analysis_id: str,
        candidate_analysis_id: str,
        job_fit_id: str,
        interview_level: str,
        max_questions: int = 6
    ) -> Dict[str, Any]:
        """Start a new interview session and generate the opening question."""
        valid_levels = ["screening", "competency", "deep_dive"]
        if interview_level not in valid_levels:
            raise ValueError(f"Invalid interview level '{interview_level}'. Must be one of: {', '.join(valid_levels)}")

        job = JobAnalysisDAO.get_by_id(job_analysis_id)
        if not job:
            raise ValueError(f"Job analysis {job_analysis_id} not found.")

        candidate = CandidateAnalysisDAO.get_by_id(candidate_analysis_id)
        if not candidate:
            raise ValueError(f"Candidate analysis {candidate_analysis_id} not found.")

        job_fit = JobFitDAO.get_by_id(job_fit_id)
        if not job_fit:
            raise ValueError(f"Job fit {job_fit_id} not found.")

        # Create session in DB
        session = InterviewSessionDAO.create(
            job_analysis_id=job_analysis_id,
            candidate_analysis_id=candidate_analysis_id,
            job_fit_id=job_fit_id,
            interview_level=interview_level,
            max_questions=max_questions
        )

        # Generate opening question
        provider = get_llm_provider()
        context = {
            "interview_level": interview_level,
            "turn_index": 0,
            "job_analysis": job,
            "candidate_analysis": candidate,
            "job_fit": job_fit,
            "weaknesses_identified": [],
            "history": []
        }
        question_data = await provider.generate_question(context)

        # Record opening turn in DB
        turn = InterviewTurnDAO.create(
            session_id=session["id"],
            turn_index=0,
            question_text=question_data["question_text"],
            question_category=question_data.get("question_category", "Opening"),
            target_competency=question_data.get("target_competency", "Role Fit")
        )

        # Update topics covered
        InterviewSessionDAO.update_state(
            session["id"],
            {
                "topics_covered": [turn["question_category"]],
                "current_question_index": 0
            }
        )

        full_session = InterviewSessionDAO.get_by_id(session["id"])
        return {
            "session": full_session,
            "current_turn": turn,
            "role_title": job["role_title"],
            "candidate_name": candidate["candidate_name"]
        }

    @staticmethod
    async def submit_answer(
        session_id: str,
        answer_text: str,
        transcript: str = "",
        audio_used: bool = False
    ) -> Dict[str, Any]:
        """
        Evaluate submitted answer, update session state, and dynamically generate next question.
        """
        session = InterviewSessionDAO.get_by_id(session_id)
        if not session:
            raise ValueError(f"Interview session {session_id} not found.")

        if session["status"] == "completed":
            raise ValueError("This interview session has already been completed.")

        turns = InterviewTurnDAO.list_by_session(session_id)
        if not turns:
            raise ValueError("No active question found for this session.")

        current_turn = turns[-1]
        if current_turn["candidate_answer"]:
            # Protect against duplicate answer submission
            raise ValueError("An answer has already been submitted for the current question.")

        job = JobAnalysisDAO.get_by_id(session["job_analysis_id"])
        candidate = CandidateAnalysisDAO.get_by_id(session["candidate_analysis_id"])

        # 1. Evaluate candidate answer
        provider = get_llm_provider()
        eval_context = {
            "question_text": current_turn["question_text"],
            "question_category": current_turn["question_category"],
            "target_competency": current_turn["target_competency"],
            "candidate_answer": answer_text,
            "job_analysis": job,
            "candidate_analysis": candidate,
            "current_difficulty": session["current_difficulty"]
        }
        eval_result = await provider.evaluate_answer(eval_context)

        # 2. Persist answer & evaluation
        evaluated_turn = InterviewTurnDAO.record_answer_and_eval(
            turn_id=current_turn["id"],
            candidate_answer=answer_text,
            candidate_transcript=transcript,
            audio_used=audio_used,
            eval_result=eval_result
        )

        # 3. Update session competencies & weaknesses
        weaknesses = list(session["weaknesses_identified"])
        strengths = list(session["strengths_identified"])
        topics = list(session["topics_covered"])

        if eval_result.get("missing_concepts"):
            for m in eval_result["missing_concepts"]:
                if m not in weaknesses:
                    weaknesses.append(m)

        if eval_result.get("score", 0) >= 75:
            strengths.append(f"{current_turn['target_competency']} on {current_turn['question_category']}")

        # Dynamic difficulty adaptation
        next_difficulty = session["current_difficulty"]
        if eval_result.get("score", 0) >= 80:
            next_difficulty = "challenging"
        elif eval_result.get("score", 0) < 60:
            next_difficulty = "fundamental"
        else:
            next_difficulty = "standard"

        next_turn_index = session["current_question_index"] + 1

        # Check if interview is finished
        if next_turn_index >= session["max_questions"]:
            InterviewSessionDAO.update_state(
                session_id,
                {
                    "status": "completed",
                    "current_difficulty": next_difficulty,
                    "current_question_index": next_turn_index,
                    "weaknesses_identified": weaknesses,
                    "strengths_identified": strengths,
                    "topics_covered": topics
                }
            )
            updated_session = InterviewSessionDAO.get_by_id(session_id)
            all_turns = InterviewTurnDAO.list_by_session(session_id)
            return {
                "session": updated_session,
                "evaluated_turn": evaluated_turn,
                "next_turn": None,
                "is_completed": True,
                "all_turns": all_turns
            }

        # 4. Generate NEXT question dynamically based on evaluation and history
        all_turns_so_far = InterviewTurnDAO.list_by_session(session_id)
        next_q_context = {
            "interview_level": session["interview_level"],
            "turn_index": next_turn_index,
            "job_analysis": job,
            "candidate_analysis": candidate,
            "weaknesses_identified": weaknesses,
            "history": all_turns_so_far,
            "current_difficulty": next_difficulty
        }
        next_q_data = await provider.generate_question(next_q_context)

        # Record next turn
        next_turn = InterviewTurnDAO.create(
            session_id=session_id,
            turn_index=next_turn_index,
            question_text=next_q_data["question_text"],
            question_category=next_q_data.get("question_category", "Follow-up"),
            target_competency=next_q_data.get("target_competency", "Technical Knowledge")
        )

        if next_turn["question_category"] not in topics:
            topics.append(next_turn["question_category"])

        InterviewSessionDAO.update_state(
            session_id,
            {
                "current_question_index": next_turn_index,
                "current_difficulty": next_difficulty,
                "weaknesses_identified": weaknesses,
                "strengths_identified": strengths,
                "topics_covered": topics
            }
        )

        updated_session = InterviewSessionDAO.get_by_id(session_id)
        all_turns = InterviewTurnDAO.list_by_session(session_id)

        return {
            "session": updated_session,
            "evaluated_turn": evaluated_turn,
            "next_turn": next_turn,
            "is_completed": False,
            "all_turns": all_turns
        }

    @staticmethod
    async def finish_session_early(session_id: str) -> Dict[str, Any]:
        """Allow candidate to finish session gracefully before reaching max questions."""
        session = InterviewSessionDAO.get_by_id(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found.")

        InterviewSessionDAO.update_state(session_id, {"status": "completed"})
        return InterviewSessionDAO.get_by_id(session_id)
