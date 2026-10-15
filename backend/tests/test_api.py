import pytest
from httpx import AsyncClient, ASGITransport
from backend.main import app
from backend.db.database import init_db


@pytest.fixture(autouse=True)
def init_database():
    init_db()


@pytest.mark.asyncio
async def test_health_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "llm_provider" in data
        assert data["database_connected"] is True


@pytest.mark.asyncio
async def test_document_paste_and_analysis_api():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # 1. Paste Job Description
        jd_res = await ac.post("/api/documents/paste", json={
            "doc_type": "job_description",
            "text": "Job Title: Senior Backend Engineer\nCompany: DataCore\nRequirements: Python, FastAPI, SQL, Docker.",
            "filename": "backend_jd.txt"
        })
        assert jd_res.status_code == 200
        jd_data = jd_res.json()
        assert jd_data["id"] != ""

        # 2. Paste Resume
        res_res = await ac.post("/api/documents/paste", json={
            "doc_type": "resume",
            "text": "Jordan Lee\nSoftware Engineer\nSkills: Python, FastAPI, Docker, PostgreSQL.\nExperience: Built backend APIs.",
            "filename": "jordan_resume.txt"
        })
        assert res_res.status_code == 200
        resume_data = res_res.json()

        # 3. Analyze Job
        job_an_res = await ac.post("/api/analysis/job", json={"document_id": jd_data["id"]})
        assert job_an_res.status_code == 200
        job_an = job_an_res.json()
        assert "Senior Backend Engineer" in job_an["role_title"]

        # 4. Analyze Candidate
        cand_an_res = await ac.post("/api/analysis/candidate", json={"document_id": resume_data["id"]})
        assert cand_an_res.status_code == 200
        cand_an = cand_an_res.json()
        assert "Jordan Lee" in cand_an["candidate_name"]

        # 5. Calculate Job Fit
        fit_res = await ac.post("/api/analysis/job-fit", json={
            "job_analysis_id": job_an["id"],
            "candidate_analysis_id": cand_an["id"]
        })
        assert fit_res.status_code == 200
        fit_data = fit_res.json()
        assert 0 <= fit_data["overall_score"] <= 100
        assert "required_skills" in fit_data["category_breakdown"]

        # 6. Start Interview
        start_res = await ac.post("/api/interview/start", json={
            "job_analysis_id": job_an["id"],
            "candidate_analysis_id": cand_an["id"],
            "job_fit_id": fit_data["id"],
            "interview_level": "screening",
            "max_questions": 3
        })
        assert start_res.status_code == 200
        session_info = start_res.json()
        session_id = session_info["session"]["id"]
        assert session_info["current_turn"]["turn_index"] == 0

        # 7. Answer Question
        ans_res = await ac.post(f"/api/interview/{session_id}/answer", json={
            "answer_text": "I have 3 years of experience writing Python services using FastAPI with automated testing.",
            "transcript": "I have 3 years of experience writing Python services using FastAPI with automated testing.",
            "audio_used": False
        })
        assert ans_res.status_code == 200
        ans_data = ans_res.json()
        assert ans_data["evaluated_turn"]["score"] > 0

        # 8. Get Session Detail
        detail_res = await ac.get(f"/api/interview/{session_id}")
        assert detail_res.status_code == 200
        detail = detail_res.json()
        assert len(detail["turns"]) >= 1

        # 9. List Recent Sessions
        recent_res = await ac.get("/api/interview/sessions/recent")
        assert recent_res.status_code == 200
        assert len(recent_res.json()) >= 1

        # 10. Report Generation and Markdown Export
        rep_res = await ac.get(f"/api/reports/{session_id}")
        assert rep_res.status_code == 200
        rep_data = rep_res.json()
        assert rep_data["overall_score"] > 0
        assert rep_data["readiness_category"] in ["NOT READY", "NEEDS PREPARATION", "INTERVIEW READY", "STRONG CANDIDATE"]

        export_res = await ac.get(f"/api/reports/{session_id}/export?format=markdown")
        assert export_res.status_code == 200
        assert "# Interview Performance Report" in export_res.text
        assert "Competency Breakdown" in export_res.text


@pytest.mark.asyncio
async def test_api_error_handling_and_file_upload():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # 1. 404 on missing document
        missing_doc = await ac.get("/api/documents/non_existent_doc_id_12345")
        assert missing_doc.status_code == 404

        # 2. 404 on missing interview session
        missing_sess = await ac.get("/api/interview/non_existent_session_id_12345")
        assert missing_sess.status_code == 404

        # 3. Validation error on paste too short (<20 chars)
        short_res = await ac.post("/api/documents/paste", json={
            "doc_type": "job_description",
            "text": "Too short",
            "filename": "short.txt"
        })
        assert short_res.status_code == 400
        assert "at least 20" in short_res.json()["detail"]

        # 4. Validation error on invalid doc_type
        bad_type = await ac.post("/api/documents/paste", json={
            "doc_type": "invalid_type",
            "text": "This is a valid length text but the document type is unsupported.",
            "filename": "test.txt"
        })
        assert bad_type.status_code == 400

        # 5. File upload via multipart/form-data
        files = {"file": ("sample_jd.txt", b"Job Title: Frontend Architect\nCompany: WebCorp\nRequirements: React, TypeScript, Redux, Webpack.", "text/plain")}
        data = {"doc_type": "job_description"}
        upload_res = await ac.post("/api/documents/upload", files=files, data=data)
        assert upload_res.status_code == 200
        assert upload_res.json()["doc_type"] == "job_description"

        # 6. File upload rejection on unsupported extension (.exe)
        bad_files = {"file": ("malicious.exe", b"MZ\x90\x00\x03\x00\x00\x00binary executable code", "application/octet-stream")}
        bad_upload = await ac.post("/api/documents/upload", files=bad_files, data=data)
        assert bad_upload.status_code == 400
        assert "not supported" in bad_upload.json()["detail"]
