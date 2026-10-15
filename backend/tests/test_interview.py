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


@pytest.mark.asyncio
async def test_adaptive_questioning_all_candidate_scenarios():
    """
    Verifies that follow-up questions dynamically and genuinely adapt to:
    - A strong, detailed answer.
    - A vague answer.
    - An answer stating that the candidate does not know.
    - An answer with an impossible or contradictory claim.
    - An empty or irrelevant answer.
    """
    doc1 = DocumentDAO.create("job_description", "jd2.txt", "Role: Systems Engineer at Apex. Needs Python, Distributed Systems, Redis.")
    doc2 = DocumentDAO.create("resume", "resume2.txt", "Candidate: John Doe. Skills: Python, Redis. Built caching systems.")
    job = JobAnalysisDAO.create(doc1["id"], {
        "role_title": "Systems Engineer",
        "company_name": "Apex",
        "summary": "Distributed systems role",
        "responsibilities": ["Build scalable caching", "Handle network partitions"],
        "required_skills": ["Python", "Redis", "Distributed Systems"],
        "preferred_skills": ["FastAPI"],
        "technical_competencies": ["Python", "Redis"],
        "behavioral_competencies": ["Problem Solving"],
        "experience_level": "3+ years",
        "education_requirements": "BS CS",
        "tools_and_frameworks": ["Redis", "Python"]
    })
    cand = CandidateAnalysisDAO.create(doc2["id"], {
        "candidate_name": "John Doe",
        "summary": "Backend dev",
        "technical_skills": ["Python", "Redis"],
        "soft_skills": ["Problem Solving"],
        "education": [{"degree": "BS CS"}],
        "experience": [{"role": "Systems Engineer"}],
        "projects": [{"title": "Cache Layer", "bullets": ["Improved latency"]}],
        "achievements": ["Deployed Redis"],
        "quantified_claims": ["Reduced latency by 45%"]
    })
    fit = JobFitDAO.create(job["id"], cand["id"], {
        "overall_score": 75,
        "required_skills_score": 80,
        "preferred_skills_score": 60,
        "project_evidence_score": 75,
        "experience_score": 75,
        "responsibility_score": 75,
        "category_breakdown": {},
        "matched_skills": [{"skill": "Python"}],
        "partial_skills": [],
        "missing_skills": [],
        "key_reasons": ["Good match"],
        "preparation_topics": ["Distributed Redis"]
    })

    # Helper to start session
    async def create_session():
        res = await InterviewEngine.start_session(
            job_analysis_id=job["id"],
            candidate_analysis_id=cand["id"],
            job_fit_id=fit["id"],
            interview_level="competency",
            max_questions=4
        )
        return res["session"]["id"]

    # Scenario 1: Strong, detailed answer -> Next question pushes deeper into scaling & failure modes
    s1 = await create_session()
    strong_ans = (
        "In our cache architecture, we used Redis cluster with master-replica replication and client-side sharding. "
        "We implemented connection pooling and pipelining, and tuned TCP keepalive settings. As a result, "
        "we reduced P99 latency by 45% under 15,000 requests per second while avoiding cache stampedes with probabilistic early expiration."
    )
    res1 = await InterviewEngine.submit_answer(s1, strong_ans)
    assert res1["evaluated_turn"]["score"] >= 80
    assert res1["next_turn"]["question_category"] == "Advanced System Scaling"
    assert "extreme load" in res1["next_turn"]["question_text"].lower()

    # Scenario 2: Vague answer -> Next question probes technical mechanics and specific libraries
    s2 = await create_session()
    vague_ans = "We just used Python and some libraries to make it work and it was pretty fast."
    res2 = await InterviewEngine.submit_answer(s2, vague_ans)
    assert res2["evaluated_turn"]["score"] <= 60
    assert res2["next_turn"]["question_category"] == "Technical Mechanics Probe"
    assert "underlying mechanics" in res2["next_turn"]["question_text"].lower()

    # Scenario 3: Incorrect technical answer -> Next question probes diagnostic correction
    s3 = await create_session()
    incorrect_ans = "We chose UDP for reliable financial transactions and ACID payment processing because TCP is too heavy."
    res3 = await InterviewEngine.submit_answer(s3, incorrect_ans)
    assert res3["evaluated_turn"]["score"] <= 40
    assert res3["next_turn"]["question_category"] == "Technical Precision & Diagnostic Correction"

    # Scenario 4: Candidate states they don't know -> Next question pivots to fundamentals & learning agility
    s4 = await create_session()
    dont_know_ans = "I honestly do not know how Redis clustering handles split-brain because I have not worked with distributed Redis."
    res4 = await InterviewEngine.submit_answer(s4, dont_know_ans)
    assert "candor" in res4["evaluated_turn"]["feedback_good"].lower()
    assert res4["next_turn"]["question_category"] == "Learning Agility & Fundamentals"
    assert "knowledge boundary" in res4["next_turn"]["question_text"].lower()

    # Scenario 5: Contradictory / impossible assertion -> Next question probes claim verification
    s5 = await create_session()
    contra_ans = "During my two month internship I single-handedly built all of the database and wrote Python from scratch."
    res5 = await InterviewEngine.submit_answer(s5, contra_ans)
    assert res5["next_turn"]["question_category"] == "Claim Verification Probe"
    assert "individual" in res5["next_turn"]["question_text"].lower()

    # Scenario 6: Irrelevant / off-topic answer -> Next question refocuses candidate
    s6 = await create_session()
    irrelevant_ans = "On weekends I really enjoy baking chocolate chip cookies, going swimming, and working on my garden."
    res6 = await InterviewEngine.submit_answer(s6, irrelevant_ans)
    assert res6["evaluated_turn"]["score"] <= 30
    assert res6["next_turn"]["question_category"] == "Core Competency Refocus"

    # Scenario 7: Empty answer -> Next question provides prompt simplification
    s7 = await create_session()
    empty_ans = "pass"
    res7 = await InterviewEngine.submit_answer(s7, empty_ans)
    assert res7["evaluated_turn"]["score"] <= 20
    assert res7["next_turn"]["question_category"] == "Prompt Clarification & Simplification"

    # Scenario 8: Short but technically correct answer -> Next question probes deeper into edge cases
    s8 = await create_session()
    concise_ans = "We configured Redis hash sets with TTL expiration for idempotent session caching."
    res8 = await InterviewEngine.submit_answer(s8, concise_ans)
    assert res8["evaluated_turn"]["score"] >= 80
    assert res8["next_turn"]["question_category"] == "Technical Deepening & Edge Cases"

    # Scenario 9: Answer that partially addresses the question -> Next question probes missing aspect
    s9 = await create_session()
    partial_ans = "I implemented the FastAPI endpoints partially, but frontend only and didn't touch the database tier."
    res9 = await InterviewEngine.submit_answer(s9, partial_ans)
    assert 55 <= res9["evaluated_turn"]["score"] <= 70
    assert res9["next_turn"]["question_category"] == "System Reliability & Missing Aspects"

    # Scenario 10: Answer demonstrating a genuine knowledge gap -> Next question bridges scaling transition
    s10 = await create_session()
    gap_ans = "In our setup we only ran a single MySQL instance on AWS RDS, so I understand read replicas in theory but never implemented automatic failover."
    res10 = await InterviewEngine.submit_answer(s10, gap_ans)
    assert 60 <= res10["evaluated_turn"]["score"] <= 75
    assert res10["next_turn"]["question_category"] == "Architectural Scaling Transition"


@pytest.mark.asyncio
async def test_external_llm_provider_fallback_handling():
    """
    Verifies that ExternalLLMProvider safely and gracefully falls back to DemoProvider
    when external credentials are missing or when an external API error occurs.
    """
    from backend.services.llm_provider import ExternalLLMProvider
    ext_provider = ExternalLLMProvider("gemini")
    assert ext_provider.is_demo is False
    assert "GEMINI" in ext_provider.name

    # Calling analyze_job with missing credentials triggers fallback without raising an exception
    job_res = await ext_provider.analyze_job("Job Title: Backend Engineer at TestCo. Needs Python and FastAPI.")
    assert job_res["role_title"] != ""
    assert any("python" in s.lower() for s in job_res["required_skills"])

    # Calling generate_question with missing credentials falls back safely
    q_res = await ext_provider.generate_question({
        "interview_level": "screening",
        "turn_index": 0,
        "job_analysis": job_res,
        "candidate_analysis": {"candidate_name": "Test Candidate", "technical_skills": ["Python"]}
    })
    assert len(q_res["question_text"]) > 10
