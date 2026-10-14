import logging
from typing import Dict, Any, List, Optional
from backend.db.models import (
    InterviewSessionDAO,
    InterviewTurnDAO,
    JobAnalysisDAO,
    CandidateAnalysisDAO,
    JobFitDAO,
    PerformanceReportDAO
)
from backend.services.llm_provider import get_llm_provider

logger = logging.getLogger(__name__)


class ReportGeneratorService:
    @staticmethod
    async def get_or_generate_report(session_id: str) -> Dict[str, Any]:
        """
        Retrieve existing report or compile a new comprehensive report from completed session turns.
        """
        # Check if already generated
        existing = PerformanceReportDAO.get_by_session(session_id)
        session = InterviewSessionDAO.get_by_id(session_id)
        if not session:
            raise ValueError(f"Interview session {session_id} not found.")

        job = JobAnalysisDAO.get_by_id(session["job_analysis_id"])
        cand = CandidateAnalysisDAO.get_by_id(session["candidate_analysis_id"])
        job_fit = JobFitDAO.get_by_id(session["job_fit_id"])

        if existing:
            existing["role_title"] = job.get("role_title", "Software Engineer") if job else "Role"
            existing["candidate_name"] = cand.get("candidate_name", "Candidate") if cand else "Candidate"
            existing["job_fit_score"] = job_fit.get("overall_score", 0) if job_fit else 0
            return existing

        turns = InterviewTurnDAO.list_by_session(session_id)
        # Filter for turns where candidate actually answered
        answered_turns = [t for t in turns if t.get("candidate_answer")]
        if not answered_turns:
            raise ValueError("Cannot generate report: No interview questions have been answered yet.")

        provider = get_llm_provider()
        report_context = {
            "session": session,
            "job_analysis": job,
            "candidate_analysis": cand,
            "job_fit": job_fit,
            "turns": answered_turns
        }

        generated_data = await provider.generate_report(report_context)

        # Persist report
        saved_report = PerformanceReportDAO.create(session_id, generated_data)
        saved_report["role_title"] = job.get("role_title", "Software Engineer") if job else "Role"
        saved_report["candidate_name"] = cand.get("candidate_name", "Candidate") if cand else "Candidate"
        saved_report["job_fit_score"] = job_fit.get("overall_score", 0) if job_fit else 0
        return saved_report
