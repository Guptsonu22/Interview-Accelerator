export type ScreenView = 'intake' | 'analysis' | 'interview' | 'report';

export interface DocumentRecord {
  id: string;
  doc_type: 'job_description' | 'resume';
  filename: string;
  char_count: number;
  parsed_metadata: Record<string, any>;
  created_at: string;
}

export interface JobAnalysis {
  id: string;
  document_id: string;
  role_title: string;
  company_name: string;
  summary: string;
  responsibilities: string[];
  required_skills: string[];
  preferred_skills: string[];
  technical_competencies: string[];
  behavioral_competencies: string[];
  experience_level: string;
  education_requirements: string;
  tools_and_frameworks: string[];
  created_at: string;
}

export interface CandidateAnalysis {
  id: string;
  document_id: string;
  candidate_name: string;
  summary: string;
  technical_skills: string[];
  soft_skills: string[];
  education: Array<{ degree: string; institution?: string }>;
  experience: Array<{ role: string; details: string }>;
  projects: Array<{ title: string; bullets?: string[]; description?: string; technologies?: string[] }>;
  achievements: string[];
  quantified_claims: string[];
  created_at: string;
}

export interface SkillMatch {
  skill: string;
  status: 'demonstrated' | 'partial' | 'missing';
  importance: 'required' | 'preferred';
  evidence: string;
}

export interface JobFitAssessment {
  id: string;
  job_analysis_id: string;
  candidate_analysis_id: string;
  overall_score: number;
  required_skills_score: number;
  preferred_skills_score: number;
  project_evidence_score: number;
  experience_score: number;
  responsibility_score: number;
  category_breakdown: Record<string, { weight: string; score: number }>;
  matched_skills: SkillMatch[];
  partial_skills: SkillMatch[];
  missing_skills: SkillMatch[];
  key_reasons: string[];
  preparation_topics: string[];
  created_at: string;
}

export interface InterviewTurn {
  id: string;
  session_id: string;
  turn_index: number;
  question_text: string;
  question_category: string;
  target_competency: string;
  candidate_answer: string;
  candidate_transcript: string;
  audio_used: number;
  score: number;
  feedback_good: string;
  feedback_improve: string;
  missing_concepts: string[];
  ideal_answer_direction: string;
  follow_up_recommendation: string;
  next_action: string;
  evaluation: Record<string, any>;
  created_at: string;
}

export interface InterviewSession {
  id: string;
  job_analysis_id: string;
  candidate_analysis_id: string;
  job_fit_id: string;
  interview_level: 'screening' | 'competency' | 'deep_dive';
  status: 'active' | 'completed' | 'cancelled';
  current_difficulty: 'fundamental' | 'standard' | 'challenging';
  current_question_index: number;
  max_questions: number;
  topics_covered: string[];
  weaknesses_identified: string[];
  strengths_identified: string[];
  created_at: string;
  updated_at: string;
}

export interface QuestionFeedbackItem {
  turn_index: number;
  question: string;
  target_competency: string;
  candidate_answer: string;
  score: number;
  feedback_good: string;
  feedback_improve: string;
  missing_concepts: string[];
  ideal_answer_direction: string;
  follow_up_recommendation: string;
}

export interface PreparationPlanItem {
  priority: number;
  topic: string;
  why_it_matters: string;
  what_to_study: string;
  practical_exercise: string;
  completion_criteria: string;
}

export interface PerformanceReport {
  id: string;
  session_id: string;
  overall_score: number;
  role_fit_score: number;
  technical_knowledge_score: number;
  problem_solving_score: number;
  communication_score: number;
  confidence_score: number;
  depth_score: number;
  behavioral_fit_score: number;
  readiness_category: 'NOT READY' | 'NEEDS PREPARATION' | 'INTERVIEW READY' | 'STRONG CANDIDATE';
  readiness_rationale: string;
  question_feedback_list: QuestionFeedbackItem[];
  demonstrated_strengths: string[];
  evidenced_weaknesses: string[];
  prioritized_prep_plan: PreparationPlanItem[];
  created_at: string;
  role_title?: string;
  candidate_name?: string;
  job_fit_score?: number;
}

export interface HealthStatus {
  status: string;
  app: string;
  version: string;
  database_connected: boolean;
  llm_provider: {
    name: string;
    is_demo_mode: boolean;
    configured_type: string;
  };
}
