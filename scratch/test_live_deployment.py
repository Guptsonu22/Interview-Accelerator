import httpx
import json
import sys

BASE_URL = "https://interview-accelerator-qt0q.onrender.com"

print(f"--- 1. Testing Health Endpoint: {BASE_URL}/api/health ---")
with httpx.Client(timeout=30.0) as client:
    health_res = client.get(f"{BASE_URL}/api/health")
    print(f"Health Status Code: {health_res.status_code}")
    print(f"Health Body: {health_res.json()}")
    assert health_res.status_code == 200
    assert health_res.json()["status"] == "ok"

    print(f"\n--- 2. Testing Frontend Root HTML: {BASE_URL}/ ---")
    root_res = client.get(f"{BASE_URL}/")
    print(f"Root Status Code: {root_res.status_code}")
    assert root_res.status_code == 200
    assert "Interview Accelerator" in root_res.text or "<div id=\"root\">" in root_res.text
    print("Frontend SPA HTML verified.")

    print(f"\n--- 3. Testing Document Intake API ---")
    jd_payload = {
        "doc_type": "job_description",
        "text": "Job Title: Senior Backend Engineer\nCompany: RenderCloud\nRequirements: Python, FastAPI, Redis, Distributed Caching, Docker, 3+ years experience.",
        "filename": "sample_jd.txt"
    }
    jd_res = client.post(f"{BASE_URL}/api/documents/paste", json=jd_payload)
    print(f"JD Paste Status: {jd_res.status_code}")
    jd_data = jd_res.json()
    assert jd_res.status_code == 200
    jd_id = jd_data["id"]

    resume_payload = {
        "doc_type": "resume",
        "text": "Candidate: Alex Rivera\nTitle: Senior Backend Developer\nSkills: Python, FastAPI, Redis, Docker, PostgreSQL.\nExperience: 4 years developing high-throughput microservices. Deployed Redis cluster handling 25,000 QPS with 99.95% uptime.",
        "filename": "sample_resume.txt"
    }
    resume_res = client.post(f"{BASE_URL}/api/documents/paste", json=resume_payload)
    print(f"Resume Paste Status: {resume_res.status_code}")
    resume_data = resume_res.json()
    assert resume_res.status_code == 200
    resume_id = resume_data["id"]

    print(f"\n--- 4. Testing Role & Candidate Analysis ---")
    job_an_res = client.post(f"{BASE_URL}/api/analysis/job", json={"document_id": jd_id})
    print(f"Job Analysis Status: {job_an_res.status_code}")
    job_an = job_an_res.json()
    print(f"Extracted Role Title: {job_an.get('role_title')}")
    print(f"Required Skills: {job_an.get('required_skills')}")
    assert job_an_res.status_code == 200

    cand_an_res = client.post(f"{BASE_URL}/api/analysis/candidate", json={"document_id": resume_id})
    print(f"Candidate Analysis Status: {cand_an_res.status_code}")
    cand_an = cand_an_res.json()
    print(f"Extracted Candidate Name: {cand_an.get('candidate_name')}")
    assert cand_an_res.status_code == 200

    print(f"\n--- 5. Testing 5-Dimension Job Fit Scoring ---")
    fit_res = client.post(f"{BASE_URL}/api/analysis/job-fit", json={
        "job_analysis_id": job_an["id"],
        "candidate_analysis_id": cand_an["id"]
    })
    print(f"Job Fit Status: {fit_res.status_code}")
    fit_data = fit_res.json()
    print(f"Overall Job Fit Score: {fit_data.get('overall_score')}/100")
    print(f"Matched Skills: {[s.get('skill') for s in fit_data.get('matched_skills', [])]}")
    assert fit_res.status_code == 200
    assert 0 <= fit_data["overall_score"] <= 100

    print(f"\n--- 6. Testing Interview Session Start & Opening Question ---")
    start_res = client.post(f"{BASE_URL}/api/interview/start", json={
        "job_analysis_id": job_an["id"],
        "candidate_analysis_id": cand_an["id"],
        "job_fit_id": fit_data["id"],
        "interview_level": "competency",
        "max_questions": 3
    })
    print(f"Interview Start Status: {start_res.status_code}")
    session_data = start_res.json()
    session_id = session_data["session"]["id"]
    opening_q = session_data["current_turn"]["question_text"]
    print(f"Opening Question: \"{opening_q}\"")
    assert start_res.status_code == 200

    print(f"\n--- 7. Testing Adaptive Answer Submission ---")
    ans_res = client.post(f"{BASE_URL}/api/interview/{session_id}/answer", json={
        "answer_text": "In our cache architecture, we deployed a Redis cluster with master-replica replication and client-side sharding. We tuned connection pooling and TCP keepalives, reducing P99 latency by 45% under 15,000 QPS while mitigating stampedes with probabilistic early expiration.",
        "transcript": "In our cache architecture, we deployed a Redis cluster with master-replica replication and client-side sharding.",
        "audio_used": True
    })
    print(f"Answer Submission Status: {ans_res.status_code}")
    ans_data = ans_res.json()
    turn_score = ans_data["evaluated_turn"]["score"]
    next_category = ans_data["next_turn"]["question_category"]
    next_q = ans_data["next_turn"]["question_text"]
    print(f"Evaluated Turn Score: {turn_score}/100")
    print(f"Adaptive Next Category: {next_category}")
    print(f"Adaptive Next Question: \"{next_q}\"")
    assert ans_res.status_code == 200
    assert turn_score >= 80

    print(f"\n--- 8. Testing Report Generation & Markdown Export ---")
    finish_res = client.post(f"{BASE_URL}/api/interview/{session_id}/finish")
    print(f"Finish Session Status: {finish_res.status_code}")
    assert finish_res.status_code == 200

    report_res = client.get(f"{BASE_URL}/api/reports/{session_id}")
    print(f"Get Report Status: {report_res.status_code}")
    report_data = report_res.json()
    print(f"Report Overall Score: {report_data.get('overall_score')}/100")
    print(f"Readiness Category: {report_data.get('readiness_category')}")
    assert report_res.status_code == 200
    assert report_data["readiness_category"] in ["STRONG CANDIDATE", "INTERVIEW READY", "NEEDS PREPARATION", "NOT READY"]

    export_res = client.get(f"{BASE_URL}/api/reports/{session_id}/export?format=markdown")
    print(f"Markdown Export Status: {export_res.status_code}")
    assert export_res.status_code == 200
    assert "# Interview Performance Report" in export_res.text or "Readiness Status" in export_res.text
    print("Markdown Report content verified.")

    print(f"\n--- 9. Testing Error Handling (404 and 422) ---")
    not_found_res = client.get(f"{BASE_URL}/api/reports/non-existent-session-id")
    print(f"Invalid Session ID Status: {not_found_res.status_code}")
    assert not_found_res.status_code == 404

    invalid_body_res = client.post(f"{BASE_URL}/api/documents/paste", json={"doc_type": "job_description", "text": "too short"})
    print(f"Invalid Payload Status: {invalid_body_res.status_code}")
    assert invalid_body_res.status_code in [400, 422]

print("\n=======================================================")
print("ALL LIVE PRODUCTION ENDPOINTS VERIFIED SUCCESSFULLY! 🚀")
print("=======================================================")
