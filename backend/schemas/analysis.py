from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class JobAnalysisRequest(BaseModel):
    document_id: str


class JobAnalysisResponse(BaseModel):
    id: str
    document_id: str
    role_title: str
    company_name: str
    summary: str
    responsibilities: List[str]
    required_skills: List[str]
    preferred_skills: List[str]
    technical_competencies: List[str]
    behavioral_competencies: List[str]
    experience_level: str
    education_requirements: str
    tools_and_frameworks: List[str]
    created_at: str


class CandidateAnalysisRequest(BaseModel):
    document_id: str


class CandidateAnalysisResponse(BaseModel):
    id: str
    document_id: str
    candidate_name: str
    summary: str
    technical_skills: List[str]
    soft_skills: List[str]
    education: List[Dict[str, Any]]
    experience: List[Dict[str, Any]]
    projects: List[Dict[str, Any]]
    achievements: List[str]
    quantified_claims: List[str]
    created_at: str


class SkillMatchItem(BaseModel):
    skill: str
    status: str  # "demonstrated", "partial", "missing"
    evidence: str
    importance: str  # "required" or "preferred"


class JobFitRequest(BaseModel):
    job_analysis_id: str
    candidate_analysis_id: str


class JobFitResponse(BaseModel):
    id: str
    job_analysis_id: str
    candidate_analysis_id: str
    overall_score: int
    required_skills_score: int
    preferred_skills_score: int
    project_evidence_score: int
    experience_score: int
    responsibility_score: int
    category_breakdown: Dict[str, Any]
    matched_skills: List[Dict[str, Any]]
    partial_skills: List[Dict[str, Any]]
    missing_skills: List[Dict[str, Any]]
    key_reasons: List[str]
    preparation_topics: List[str]
    created_at: str
