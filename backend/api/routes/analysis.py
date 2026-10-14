from fastapi import APIRouter, HTTPException, status
from backend.schemas.analysis import (
    JobAnalysisRequest,
    JobAnalysisResponse,
    CandidateAnalysisRequest,
    CandidateAnalysisResponse,
    JobFitRequest,
    JobFitResponse
)
from backend.db.models import (
    DocumentDAO,
    JobAnalysisDAO,
    CandidateAnalysisDAO,
    JobFitDAO
)
from backend.services.llm_provider import get_llm_provider
from backend.services.job_fit import JobFitService

router = APIRouter(prefix="/api/analysis", tags=["Analysis"])


@router.post("/job", response_model=JobAnalysisResponse)
async def analyze_job_document(payload: JobAnalysisRequest):
    doc = DocumentDAO.get_by_id(payload.document_id)
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job description document not found.")

    provider = get_llm_provider()
    analysis_data = await provider.analyze_job(doc["raw_text"])
    created = JobAnalysisDAO.create(payload.document_id, analysis_data)
    return created


@router.get("/job/{analysis_id}", response_model=JobAnalysisResponse)
async def get_job_analysis(analysis_id: str):
    record = JobAnalysisDAO.get_by_id(analysis_id)
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job analysis not found.")
    return record


@router.post("/candidate", response_model=CandidateAnalysisResponse)
async def analyze_candidate_document(payload: CandidateAnalysisRequest):
    doc = DocumentDAO.get_by_id(payload.document_id)
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume document not found.")

    provider = get_llm_provider()
    analysis_data = await provider.analyze_resume(doc["raw_text"])
    created = CandidateAnalysisDAO.create(payload.document_id, analysis_data)
    return created


@router.get("/candidate/{analysis_id}", response_model=CandidateAnalysisResponse)
async def get_candidate_analysis(analysis_id: str):
    record = CandidateAnalysisDAO.get_by_id(analysis_id)
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Candidate analysis not found.")
    return record


@router.post("/job-fit", response_model=JobFitResponse)
async def calculate_job_fit(payload: JobFitRequest):
    job = JobAnalysisDAO.get_by_id(payload.job_analysis_id)
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job analysis not found.")

    candidate = CandidateAnalysisDAO.get_by_id(payload.candidate_analysis_id)
    if not candidate:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Candidate analysis not found.")

    fit_data = JobFitService.calculate_job_fit(job, candidate)
    created = JobFitDAO.create(payload.job_analysis_id, payload.candidate_analysis_id, fit_data)
    return created


@router.get("/job-fit/{fit_id}", response_model=JobFitResponse)
async def get_job_fit(fit_id: str):
    record = JobFitDAO.get_by_id(fit_id)
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job fit assessment not found.")
    return record
