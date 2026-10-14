import pytest
from backend.db.database import init_db
from backend.db.models import (
    DocumentDAO,
    JobAnalysisDAO,
    CandidateAnalysisDAO,
    JobFitDAO,
    InterviewSessionDAO,
    InterviewTurnDAO
)
from backend.services.interview_engine import InterviewEngine
from backend.services.report_generator import ReportGeneratorService


@pytest.fixture(autouse=True)
def setup_database():
    init_db()


@pytest.mark.asyncio
async def test_interview_full_flow():
    # Setup test entities
    doc1 = DocumentDAO.create("job_description", "jd.txt", "Role: Python AI Engineer at NovaTech. Needs Python, FastAPI, React.")
    doc2 = DocumentDAO.create("resume", "resume.txt", "Candidate: Sarah Connor. Skills: Python, FastAPI, Docker. Built scalable APIs.")

    job = JobAnalysisDAO.create(doc1["id"], {
        "role_title": "Python AI Engineer",
        "company_name": "NovaTech",
        "summary": "AI role",
        "responsibilities": ["Build scalable APIs", "Deploy models"],
        "required_skills": ["Python", "FastAPI"],
        "preferred_skills": ["React"],
        "technical_competencies": ["Python", "FastAPI"],
        "behavioral_competencies": ["Communication"],
        "experience_level": "2+ years",
        "education_requirements": "BS CS",
        "tools_and_frameworks": ["FastAPI", "Docker"]
    })

    cand = CandidateAnalysisDAO.create(doc2["id"], {
        "candidate_name": "Sarah Connor",
        "summary": "Experienced engineer",
        "technical_skills": ["Python", "FastAPI", "Docker"],
        "soft_skills": ["Communication", "Problem Solving"],
        "education": [{"degree": "BS CS"}],
        "experience": [{"role": "Backend Dev"}],
        "projects": [{"title": "API Gateway", "bullets": ["Improved latency by 40%"]}],
        "achievements": ["Delivered production services"],
        "quantified_claims": ["Improved latency by 40%"]
    })

    fit = JobFitDAO.create(job["id"], cand["id"], {
        "overall_score": 82,
        "required_skills_score": 90,
        "preferred_skills_score": 70,
        "project_evidence_score": 85,
        "experience_score": 80,
        "responsibility_score": 85,
        "category_breakdown": {},
        "matched_skills": [{"skill": "Python"}],
        "partial_skills": [],
        "missing_skills": [],
        "key_reasons": ["High alignment"],
        "preparation_topics": ["Docker profiling"]
    })

    # Test all 3 levels: Screening, Competency, Deep-Dive
    for level in ["screening", "competency", "deep_dive"]:
        init_res = await InterviewEngine.start_session(
            job_analysis_id=job["id"],
            candidate_analysis_id=cand["id"],
            job_fit_id=fit["id"],
            interview_level=level,
            max_questions=3
        )
        session = init_res["session"]
        turn = init_res["current_turn"]

        assert session["interview_level"] == level
        assert session["status"] == "active"
        assert turn["turn_index"] == 0
        assert len(turn["question_text"]) > 15

        # Answer question 1
        ans1 = "In my previous project, I designed the REST endpoints using FastAPI and async handlers, which reduced latency by 40%."
        sub1 = await InterviewEngine.submit_answer(session["id"], ans1)
        assert sub1["evaluated_turn"]["score"] > 0
        assert sub1["evaluated_turn"]["feedback_good"] != ""
        assert sub1["next_turn"] is not None
        assert sub1["next_turn"]["turn_index"] == 1

        # Answer question 2
        ans2 = "I implemented Redis caching with a TTL strategy and database connection pooling to handle concurrency safely."
        sub2 = await InterviewEngine.submit_answer(session["id"], ans2)
        assert sub2["next_turn"]["turn_index"] == 2

        # Answer question 3 (final question in a 3-question session)
        ans3 = "For failure handling, I implemented the circuit breaker pattern with backoff retries so downstream outages do not cascade."
        sub3 = await InterviewEngine.submit_answer(session["id"], ans3)
        assert sub3["is_completed"] is True
        assert sub3["session"]["status"] == "completed"

        # Prevent duplicate answer when session is completed
        with pytest.raises(ValueError, match="already been completed"):
            await InterviewEngine.submit_answer(session["id"], "Extra try on completed session")

        # Generate and verify performance report
        report = await ReportGeneratorService.get_or_generate_report(session["id"])
        assert report["overall_score"] > 0
        assert report["role_fit_score"] > 0
        assert report["technical_knowledge_score"] > 0
        assert report["problem_solving_score"] > 0
        assert report["communication_score"] > 0
        assert report["confidence_score"] > 0
        assert report["depth_score"] > 0
        assert report["behavioral_fit_score"] > 0
        assert report["readiness_category"] in ["NOT READY", "NEEDS PREPARATION", "INTERVIEW READY", "STRONG CANDIDATE"]
        assert len(report["question_feedback_list"]) == 3
        assert len(report["demonstrated_strengths"]) > 0
        assert len(report["prioritized_prep_plan"]) == 3
