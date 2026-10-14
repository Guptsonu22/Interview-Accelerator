import json
import uuid
from typing import Dict, Any, List, Optional
from backend.db.database import get_db_connection


class DocumentDAO:
    @staticmethod
    def create(doc_type: str, filename: str, raw_text: str, parsed_metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        doc_id = str(uuid.uuid4())
        meta_json = json.dumps(parsed_metadata or {})
        with get_db_connection() as conn:
            conn.execute(
                """
                INSERT INTO documents (id, doc_type, filename, raw_text, char_count, parsed_metadata)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (doc_id, doc_type, filename, raw_text, len(raw_text), meta_json)
            )
        return DocumentDAO.get_by_id(doc_id)

    @staticmethod
    def get_by_id(doc_id: str) -> Optional[Dict[str, Any]]:
        with get_db_connection() as conn:
            row = conn.execute("SELECT * FROM documents WHERE id = ?", (doc_id,)).fetchone()
            if not row:
                return None
            data = dict(row)
            data["parsed_metadata"] = json.loads(data["parsed_metadata"])
            return data


class JobAnalysisDAO:
    @staticmethod
    def create(document_id: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        analysis_id = str(uuid.uuid4())
        with get_db_connection() as conn:
            conn.execute(
                """
                INSERT INTO job_analyses (
                    id, document_id, role_title, company_name, summary,
                    responsibilities, required_skills, preferred_skills,
                    technical_competencies, behavioral_competencies,
                    experience_level, education_requirements, tools_and_frameworks
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    analysis_id,
                    document_id,
                    analysis.get("role_title", "Unknown Role"),
                    analysis.get("company_name", "Not specified"),
                    analysis.get("summary", ""),
                    json.dumps(analysis.get("responsibilities", [])),
                    json.dumps(analysis.get("required_skills", [])),
                    json.dumps(analysis.get("preferred_skills", [])),
                    json.dumps(analysis.get("technical_competencies", [])),
                    json.dumps(analysis.get("behavioral_competencies", [])),
                    analysis.get("experience_level", "Not specified"),
                    analysis.get("education_requirements", "Not specified"),
                    json.dumps(analysis.get("tools_and_frameworks", [])),
                )
            )
        return JobAnalysisDAO.get_by_id(analysis_id)

    @staticmethod
    def get_by_id(analysis_id: str) -> Optional[Dict[str, Any]]:
        with get_db_connection() as conn:
            row = conn.execute("SELECT * FROM job_analyses WHERE id = ?", (analysis_id,)).fetchone()
            if not row:
                return None
            res = dict(row)
            for key in ["responsibilities", "required_skills", "preferred_skills", "technical_competencies", "behavioral_competencies", "tools_and_frameworks"]:
                res[key] = json.loads(res[key])
            return res


class CandidateAnalysisDAO:
    @staticmethod
    def create(document_id: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        analysis_id = str(uuid.uuid4())
        with get_db_connection() as conn:
            conn.execute(
                """
                INSERT INTO candidate_analyses (
                    id, document_id, candidate_name, summary,
                    technical_skills, soft_skills, education, experience,
                    projects, achievements, quantified_claims
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    analysis_id,
                    document_id,
                    analysis.get("candidate_name", "Candidate"),
                    analysis.get("summary", ""),
                    json.dumps(analysis.get("technical_skills", [])),
                    json.dumps(analysis.get("soft_skills", [])),
                    json.dumps(analysis.get("education", [])),
                    json.dumps(analysis.get("experience", [])),
                    json.dumps(analysis.get("projects", [])),
                    json.dumps(analysis.get("achievements", [])),
                    json.dumps(analysis.get("quantified_claims", [])),
                )
            )
        return CandidateAnalysisDAO.get_by_id(analysis_id)

    @staticmethod
    def get_by_id(analysis_id: str) -> Optional[Dict[str, Any]]:
        with get_db_connection() as conn:
            row = conn.execute("SELECT * FROM candidate_analyses WHERE id = ?", (analysis_id,)).fetchone()
            if not row:
                return None
            res = dict(row)
            for key in ["technical_skills", "soft_skills", "education", "experience", "projects", "achievements", "quantified_claims"]:
                res[key] = json.loads(res[key])
            return res


class JobFitDAO:
    @staticmethod
    def create(job_analysis_id: str, candidate_analysis_id: str, fit_data: Dict[str, Any]) -> Dict[str, Any]:
        fit_id = str(uuid.uuid4())
        with get_db_connection() as conn:
            conn.execute(
                """
                INSERT INTO job_fit_assessments (
                    id, job_analysis_id, candidate_analysis_id,
                    overall_score, required_skills_score, preferred_skills_score,
                    project_evidence_score, experience_score, responsibility_score,
                    category_breakdown, matched_skills, partial_skills, missing_skills,
                    key_reasons, preparation_topics
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    fit_id,
                    job_analysis_id,
                    candidate_analysis_id,
                    fit_data.get("overall_score", 0),
                    fit_data.get("required_skills_score", 0),
                    fit_data.get("preferred_skills_score", 0),
                    fit_data.get("project_evidence_score", 0),
                    fit_data.get("experience_score", 0),
                    fit_data.get("responsibility_score", 0),
                    json.dumps(fit_data.get("category_breakdown", {})),
                    json.dumps(fit_data.get("matched_skills", [])),
                    json.dumps(fit_data.get("partial_skills", [])),
                    json.dumps(fit_data.get("missing_skills", [])),
                    json.dumps(fit_data.get("key_reasons", [])),
                    json.dumps(fit_data.get("preparation_topics", [])),
                )
            )
        return JobFitDAO.get_by_id(fit_id)

    @staticmethod
    def get_by_id(fit_id: str) -> Optional[Dict[str, Any]]:
        with get_db_connection() as conn:
            row = conn.execute("SELECT * FROM job_fit_assessments WHERE id = ?", (fit_id,)).fetchone()
            if not row:
                return None
            res = dict(row)
            res["category_breakdown"] = json.loads(res["category_breakdown"])
            for key in ["matched_skills", "partial_skills", "missing_skills", "key_reasons", "preparation_topics"]:
                res[key] = json.loads(res[key])
            return res


class InterviewSessionDAO:
    @staticmethod
    def create(job_analysis_id: str, candidate_analysis_id: str, job_fit_id: str, interview_level: str, max_questions: int = 6) -> Dict[str, Any]:
        session_id = str(uuid.uuid4())
        with get_db_connection() as conn:
            conn.execute(
                """
                INSERT INTO interview_sessions (
                    id, job_analysis_id, candidate_analysis_id, job_fit_id,
                    interview_level, status, current_difficulty, current_question_index,
                    max_questions, topics_covered, weaknesses_identified, strengths_identified
                ) VALUES (?, ?, ?, ?, ?, 'active', 'standard', 0, ?, '[]', '[]', '[]')
                """,
                (session_id, job_analysis_id, candidate_analysis_id, job_fit_id, interview_level, max_questions)
            )
        return InterviewSessionDAO.get_by_id(session_id)

    @staticmethod
    def get_by_id(session_id: str) -> Optional[Dict[str, Any]]:
        with get_db_connection() as conn:
            row = conn.execute("SELECT * FROM interview_sessions WHERE id = ?", (session_id,)).fetchone()
            if not row:
                return None
            res = dict(row)
            res["topics_covered"] = json.loads(res["topics_covered"])
            res["weaknesses_identified"] = json.loads(res["weaknesses_identified"])
            res["strengths_identified"] = json.loads(res["strengths_identified"])
            return res

    @staticmethod
    def update_state(session_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        fields = []
        values = []
        for key, val in updates.items():
            if key in ["topics_covered", "weaknesses_identified", "strengths_identified"]:
                fields.append(f"{key} = ?")
                values.append(json.dumps(val))
            elif key in ["status", "current_difficulty", "current_question_index"]:
                fields.append(f"{key} = ?")
                values.append(val)
        fields.append("updated_at = CURRENT_TIMESTAMP")
        values.append(session_id)

        query = f"UPDATE interview_sessions SET {', '.join(fields)} WHERE id = ?"
        with get_db_connection() as conn:
            conn.execute(query, tuple(values))
        return InterviewSessionDAO.get_by_id(session_id)

    @staticmethod
    def list_recent(limit: int = 10) -> List[Dict[str, Any]]:
        with get_db_connection() as conn:
            rows = conn.execute(
                """
                SELECT s.*, j.role_title, j.company_name, c.candidate_name, r.overall_score as final_score
                FROM interview_sessions s
                LEFT JOIN job_analyses j ON s.job_analysis_id = j.id
                LEFT JOIN candidate_analyses c ON s.candidate_analysis_id = c.id
                LEFT JOIN performance_reports r ON s.id = r.session_id
                ORDER BY s.created_at DESC
                LIMIT ?
                """,
                (limit,)
            ).fetchall()
            result = []
            for r in rows:
                item = dict(r)
                item["topics_covered"] = json.loads(item["topics_covered"])
                item["weaknesses_identified"] = json.loads(item["weaknesses_identified"])
                item["strengths_identified"] = json.loads(item["strengths_identified"])
                result.append(item)
            return result


class InterviewTurnDAO:
    @staticmethod
    def create(session_id: str, turn_index: int, question_text: str, question_category: str, target_competency: str) -> Dict[str, Any]:
        turn_id = str(uuid.uuid4())
        with get_db_connection() as conn:
            conn.execute(
                """
                INSERT INTO interview_turns (
                    id, session_id, turn_index, question_text, question_category, target_competency
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (turn_id, session_id, turn_index, question_text, question_category, target_competency)
            )
        return InterviewTurnDAO.get_by_id(turn_id)

    @staticmethod
    def get_by_id(turn_id: str) -> Optional[Dict[str, Any]]:
        with get_db_connection() as conn:
            row = conn.execute("SELECT * FROM interview_turns WHERE id = ?", (turn_id,)).fetchone()
            if not row:
                return None
            res = dict(row)
            res["evaluation"] = json.loads(res["evaluation"])
            res["missing_concepts"] = json.loads(res["missing_concepts"])
            return res

    @staticmethod
    def list_by_session(session_id: str) -> List[Dict[str, Any]]:
        with get_db_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM interview_turns WHERE session_id = ? ORDER BY turn_index ASC",
                (session_id,)
            ).fetchall()
            results = []
            for r in rows:
                item = dict(r)
                item["evaluation"] = json.loads(item["evaluation"])
                item["missing_concepts"] = json.loads(item["missing_concepts"])
                results.append(item)
            return results

    @staticmethod
    def record_answer_and_eval(
        turn_id: str,
        candidate_answer: str,
        candidate_transcript: str,
        audio_used: bool,
        eval_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        with get_db_connection() as conn:
            conn.execute(
                """
                UPDATE interview_turns SET
                    candidate_answer = ?,
                    candidate_transcript = ?,
                    audio_used = ?,
                    evaluation = ?,
                    score = ?,
                    feedback_good = ?,
                    feedback_improve = ?,
                    missing_concepts = ?,
                    ideal_answer_direction = ?,
                    follow_up_recommendation = ?,
                    next_action = ?
                WHERE id = ?
                """,
                (
                    candidate_answer,
                    candidate_transcript,
                    1 if audio_used else 0,
                    json.dumps(eval_result.get("rubric_breakdown", {})),
                    eval_result.get("score", 0),
                    eval_result.get("feedback_good", ""),
                    eval_result.get("feedback_improve", ""),
                    json.dumps(eval_result.get("missing_concepts", [])),
                    eval_result.get("ideal_answer_direction", ""),
                    eval_result.get("follow_up_recommendation", ""),
                    eval_result.get("next_action", "continue"),
                    turn_id
                )
            )
        return InterviewTurnDAO.get_by_id(turn_id)


class PerformanceReportDAO:
    @staticmethod
    def create(session_id: str, report_data: Dict[str, Any]) -> Dict[str, Any]:
        report_id = str(uuid.uuid4())
        with get_db_connection() as conn:
            conn.execute(
                """
                INSERT INTO performance_reports (
                    id, session_id, overall_score,
                    role_fit_score, technical_knowledge_score, problem_solving_score,
                    communication_score, confidence_score, depth_score, behavioral_fit_score,
                    readiness_category, readiness_rationale,
                    question_feedback_list, demonstrated_strengths,
                    evidenced_weaknesses, prioritized_prep_plan
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    report_id,
                    session_id,
                    report_data.get("overall_score", 0),
                    report_data.get("role_fit_score", 0),
                    report_data.get("technical_knowledge_score", 0),
                    report_data.get("problem_solving_score", 0),
                    report_data.get("communication_score", 0),
                    report_data.get("confidence_score", 0),
                    report_data.get("depth_score", 0),
                    report_data.get("behavioral_fit_score", 0),
                    report_data.get("readiness_category", "NEEDS PREPARATION"),
                    report_data.get("readiness_rationale", ""),
                    json.dumps(report_data.get("question_feedback_list", [])),
                    json.dumps(report_data.get("demonstrated_strengths", [])),
                    json.dumps(report_data.get("evidenced_weaknesses", [])),
                    json.dumps(report_data.get("prioritized_prep_plan", [])),
                )
            )
        return PerformanceReportDAO.get_by_session(session_id)

    @staticmethod
    def get_by_session(session_id: str) -> Optional[Dict[str, Any]]:
        with get_db_connection() as conn:
            row = conn.execute("SELECT * FROM performance_reports WHERE session_id = ?", (session_id,)).fetchone()
            if not row:
                return None
            res = dict(row)
            res["question_feedback_list"] = json.loads(res["question_feedback_list"])
            res["demonstrated_strengths"] = json.loads(res["demonstrated_strengths"])
            res["evidenced_weaknesses"] = json.loads(res["evidenced_weaknesses"])
            res["prioritized_prep_plan"] = json.loads(res["prioritized_prep_plan"])
            return res
