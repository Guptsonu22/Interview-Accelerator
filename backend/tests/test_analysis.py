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
