from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class InterviewStartRequest(BaseModel):
    job_analysis_id: str
    candidate_analysis_id: str
    job_fit_id: str
    interview_level: str = Field(..., description="'screening', 'competency', or 'deep_dive'")
    max_questions: Optional[int] = Field(default=6, ge=3, le=10)


class InterviewSessionResponse(BaseModel):
    id: str
    job_analysis_id: str
    candidate_analysis_id: str
    job_fit_id: str
    interview_level: str
    status: str
    current_difficulty: str
    current_question_index: int
    max_questions: int
    topics_covered: List[str]
    weaknesses_identified: List[str]
    strengths_identified: List[str]
    created_at: str
    updated_at: str


class AnswerSubmitRequest(BaseModel):
    answer_text: str = Field(..., min_length=2, max_length=10000)
    transcript: Optional[str] = Field(default="")
    audio_used: Optional[bool] = Field(default=False)


class InterviewTurnResponse(BaseModel):
    id: str
    session_id: str
    turn_index: int
    question_text: str
    question_category: str
    target_competency: str
    candidate_answer: str
    candidate_transcript: str
    audio_used: int
    score: int
    feedback_good: str
    feedback_improve: str
    missing_concepts: List[str]
    ideal_answer_direction: str
    follow_up_recommendation: str
    next_action: str
    evaluation: Dict[str, Any]
    created_at: str


class SessionDetailResponse(BaseModel):
    session: InterviewSessionResponse
    turns: List[InterviewTurnResponse]
    current_turn: Optional[InterviewTurnResponse] = None
    role_title: Optional[str] = None
    candidate_name: Optional[str] = None
