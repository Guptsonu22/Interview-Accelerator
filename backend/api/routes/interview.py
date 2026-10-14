from fastapi import APIRouter, HTTPException, status
from backend.schemas.interview import (
    InterviewStartRequest,
    InterviewSessionResponse,
    AnswerSubmitRequest,
    InterviewTurnResponse,
    SessionDetailResponse
)
from backend.db.models import (
    InterviewSessionDAO,
    InterviewTurnDAO,
    JobAnalysisDAO,
    CandidateAnalysisDAO
)
from backend.services.interview_engine import InterviewEngine

router = APIRouter(prefix="/api/interview", tags=["Interview"])


@router.post("/start")
async def start_interview_session(payload: InterviewStartRequest):
    try:
        result = await InterviewEngine.start_session(
            job_analysis_id=payload.job_analysis_id,
            candidate_analysis_id=payload.candidate_analysis_id,
            job_fit_id=payload.job_fit_id,
            interview_level=payload.interview_level,
            max_questions=payload.max_questions or 6
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to start interview: {str(e)}")


@router.get("/sessions/recent")
async def list_recent_sessions(limit: int = 10):
    return InterviewSessionDAO.list_recent(limit=limit)


@router.get("/{session_id}", response_model=SessionDetailResponse)
async def get_session_detail(session_id: str):
    session = InterviewSessionDAO.get_by_id(session_id)
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Interview session not found.")

    turns = InterviewTurnDAO.list_by_session(session_id)
    current_turn = turns[-1] if turns else None
    
    job = JobAnalysisDAO.get_by_id(session["job_analysis_id"])
    candidate = CandidateAnalysisDAO.get_by_id(session["candidate_analysis_id"])

    return {
        "session": session,
        "turns": turns,
        "current_turn": current_turn,
        "role_title": job["role_title"] if job else None,
        "candidate_name": candidate["candidate_name"] if candidate else None
    }


@router.post("/{session_id}/answer")
async def submit_candidate_answer(session_id: str, payload: AnswerSubmitRequest):
    try:
        result = await InterviewEngine.submit_answer(
            session_id=session_id,
            answer_text=payload.answer_text,
            transcript=payload.transcript or "",
            audio_used=payload.audio_used or False
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Answer processing error: {str(e)}")


@router.post("/{session_id}/finish")
async def finish_interview_session(session_id: str):
    try:
        updated = await InterviewEngine.finish_session_early(session_id)
        return updated
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
