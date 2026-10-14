from typing import List, Dict, Any, Optional
from pydantic import BaseModel


class QuestionFeedbackItem(BaseModel):
    turn_index: int
    question: str
    target_competency: str
    candidate_answer: str
    score: int
    feedback_good: str
    feedback_improve: str
    missing_concepts: List[str]
    ideal_answer_direction: str
    follow_up_recommendation: str


class PreparationPlanItem(BaseModel):
    priority: int  # 1 = Highest
    topic: str
    why_it_matters: str
    what_to_study: str
    practical_exercise: str
    completion_criteria: str


class PerformanceReportResponse(BaseModel):
    id: str
    session_id: str
    overall_score: int
    role_fit_score: int
    technical_knowledge_score: int
    problem_solving_score: int
    communication_score: int
    confidence_score: int
    depth_score: int
    behavioral_fit_score: int
    readiness_category: str  # "NOT READY", "NEEDS PREPARATION", "INTERVIEW READY", "STRONG CANDIDATE"
    readiness_rationale: str
    question_feedback_list: List[Dict[str, Any]]
    demonstrated_strengths: List[str]
    evidenced_weaknesses: List[str]
    prioritized_prep_plan: List[Dict[str, Any]]
    created_at: str
    role_title: Optional[str] = None
    candidate_name: Optional[str] = None
    job_fit_score: Optional[int] = None
