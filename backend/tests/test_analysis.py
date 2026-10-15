import pytest
from backend.services.llm_provider import DemoProvider
from backend.services.job_fit import JobFitService

SAMPLE_JD = """
Job Title: Full Stack AI Engineer
Company: CloudScale AI
Responsibilities:
- Build, test, and deploy responsive React web applications.
- Develop scalable backend APIs with Python, FastAPI, and PostgreSQL.
- Integrate AI language models and prompt pipelines.
- Write automated unit and integration tests with pytest.
Requirements:
- 3+ years of experience with Python, FastAPI, React, and TypeScript.
- Strong knowledge of RESTful API design, database schemas, and Docker.
- Experience with Git, CI/CD pipelines, and cloud deployment.
Preferred:
- Experience with Kubernetes and Redis caching.
- Familiarity with Web Speech API and voice synthesis.
"""

SAMPLE_RESUME = """
Alex Chen
Full Stack Developer
Summary: Experienced software developer building high-performance web applications and AI tools.
Skills: Python, FastAPI, React, TypeScript, JavaScript, PostgreSQL, Docker, Git, Pytest, REST, Tailwind.
Experience:
Software Engineer at TechFlow (2022 - Present)
- Developed real-time microservices using Python and FastAPI, reducing response latency by 35%.
- Implemented frontend interfaces in React and TypeScript serving 50,000 monthly active users.
Projects:
Interview Accelerator Web Application
- Built adaptive mock interview platform using FastAPI backend and Vite React frontend.
- Incorporated deterministic scoring rubrics and Web Speech transcription.
Education:
B.S. in Computer Science, University of Technology (2022)
"""


@pytest.mark.asyncio
async def test_job_analysis_extraction():
    provider = DemoProvider()
    analysis = await provider.analyze_job(SAMPLE_JD)

    assert analysis["role_title"] != ""
    assert "CloudScale AI" in analysis["company_name"] or analysis["company_name"] != "Not specified"
    assert len(analysis["responsibilities"]) >= 2
    assert any("python" in s.lower() for s in analysis["required_skills"])
    assert any("react" in s.lower() for s in analysis["required_skills"])


@pytest.mark.asyncio
async def test_candidate_analysis_extraction():
    provider = DemoProvider()
    analysis = await provider.analyze_resume(SAMPLE_RESUME)

    assert "Alex Chen" in analysis["candidate_name"]
    assert any("python" in s.lower() for s in analysis["technical_skills"])
    assert any("react" in s.lower() for s in analysis["technical_skills"])
    assert len(analysis["quantified_claims"]) >= 1


@pytest.mark.asyncio
async def test_job_fit_deterministic_calculation():
    provider = DemoProvider()
    job = await provider.analyze_job(SAMPLE_JD)
    cand = await provider.analyze_resume(SAMPLE_RESUME)

    fit1 = JobFitService.calculate_job_fit(job, cand)
    fit2 = JobFitService.calculate_job_fit(job, cand)

    # 1. Reproducibility test: same inputs must yield identical scores
    assert fit1["overall_score"] == fit2["overall_score"]
    assert fit1["required_skills_score"] == fit2["required_skills_score"]
    assert fit1["category_breakdown"] == fit2["category_breakdown"]

    # 2. Score bounds test: 0 <= score <= 100
    assert 0 <= fit1["overall_score"] <= 100
    assert 0 <= fit1["required_skills_score"] <= 100

    # 3. Category evidence test: matched, partial, missing must be distinct
    assert len(fit1["matched_skills"]) > 0
    assert len(fit1["key_reasons"]) > 0
    assert len(fit1["preparation_topics"]) > 0


@pytest.mark.asyncio
async def test_job_fit_edge_cases_empty_and_unrelated():
    provider = DemoProvider()
    job = await provider.analyze_job(SAMPLE_JD)

    # 1. Edge Case: Completely empty candidate profile
    empty_cand = {
        "candidate_name": "Unknown",
        "technical_skills": [],
        "soft_skills": [],
        "education": [],
        "experience": [],
        "projects": [],
        "quantified_claims": []
    }
    empty_fit = JobFitService.calculate_job_fit(job, empty_cand)
    assert empty_fit["overall_score"] == 0
    assert empty_fit["required_skills_score"] == 0
    assert empty_fit["project_evidence_score"] == 0
    assert empty_fit["experience_score"] == 0
    assert len(empty_fit["missing_skills"]) > 0

    # 2. Edge Case: Completely unrelated profile (e.g. Culinary background)
    unrelated_cand = {
        "candidate_name": "Chef Mario",
        "technical_skills": ["Pastry Making", "Sauce Reduction", "Kitchen Inventory"],
        "soft_skills": ["Menu Planning"],
        "education": [{"degree": "Culinary Arts"}],
        "experience": [{"role": "Executive Chef", "details": "Managed restaurant dinner rush"}],
        "projects": [{"title": "Seasonal Menu Launch", "bullets": ["Designed 15 new dishes"]}],
        "quantified_claims": ["Served 400 covers nightly"]
    }
    unrelated_fit = JobFitService.calculate_job_fit(job, unrelated_cand)
    assert unrelated_fit["overall_score"] < 25
    assert unrelated_fit["required_skills_score"] == 0
    assert len(unrelated_fit["missing_skills"]) >= len(job["required_skills"])


@pytest.mark.asyncio
async def test_distinct_profiles_produce_different_analysis_and_questions():
    """
    Verifies that substantially different JD/resume pairs (e.g. Mobile iOS vs Data Platform)
    produce distinct analysis results, different job fit scores, and tailored questions.
    """
    provider = DemoProvider()

    # Profile A: iOS Mobile Engineer
    jd_ios = "Job Title: Senior iOS Engineer\nCompany: SwiftMobile\nRequirements: Swift, SwiftUI, Combine, CoreData."
    resume_ios = "Elena Rostova\nMobile Engineer\nSkills: Swift, SwiftUI, Combine, iOS.\nProjects: HealthTracker iOS App."

    # Profile B: Data Platform Engineer
    jd_data = "Job Title: Data Platform Engineer\nCompany: DataLake Inc\nRequirements: Apache Spark, Kafka, Snowflake, Python."
    resume_data = "Marcus Vance\nData Engineer\nSkills: Apache Spark, Kafka, Snowflake, Python, SQL.\nProjects: Real-time Streaming Pipeline."

    job_ios = await provider.analyze_job(jd_ios)
    cand_ios = await provider.analyze_resume(resume_ios)
    fit_ios = JobFitService.calculate_job_fit(job_ios, cand_ios)

    job_data = await provider.analyze_job(jd_data)
    cand_data = await provider.analyze_resume(resume_data)
    fit_data = JobFitService.calculate_job_fit(job_data, cand_data)

    # Cross-match: Elena applying for Data Platform should have a low score
    cross_fit = JobFitService.calculate_job_fit(job_data, cand_ios)

    assert "Senior iOS Engineer" in job_ios["role_title"]
    assert "Data Platform Engineer" in job_data["role_title"]
    assert job_ios["role_title"] != job_data["role_title"]

    assert fit_ios["overall_score"] >= 60
    assert fit_data["overall_score"] >= 60
    assert cross_fit["overall_score"] < 40  # Swift engineer in Data platform role has low fit

    # Compare generated questions
    q_ios = await provider.generate_question({
        "interview_level": "competency",
        "turn_index": 0,
        "job_analysis": job_ios,
        "candidate_analysis": cand_ios
    })
    q_data = await provider.generate_question({
        "interview_level": "competency",
        "turn_index": 0,
        "job_analysis": job_data,
        "candidate_analysis": cand_data
    })

    assert q_ios["question_text"] != q_data["question_text"]
    assert "swift" in q_ios["question_text"].lower() or "mobile" in q_ios["question_text"].lower() or "architecture" in q_ios["question_text"].lower()
    assert "spark" in q_data["question_text"].lower() or "kafka" in q_data["question_text"].lower() or "architecture" in q_data["question_text"].lower()
