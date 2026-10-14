import {
  DocumentRecord,
  JobAnalysis,
  CandidateAnalysis,
  JobFitAssessment,
  InterviewSession,
  InterviewTurn,
  PerformanceReport,
  HealthStatus
} from '../types';

const API_BASE = 'http://127.0.0.1:8000/api';

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    let errorMsg = `Server error (${res.status})`;
    try {
      const errJson = await res.json();
      if (errJson.detail) {
        errorMsg = typeof errJson.detail === 'string' ? errJson.detail : JSON.stringify(errJson.detail);
      }
    } catch {
      errorMsg = await res.text();
    }
    throw new Error(errorMsg || `Request failed with status ${res.status}`);
  }
  return res.json() as Promise<T>;
}

export const api = {
  async getHealth(): Promise<HealthStatus> {
    const res = await fetch(`${API_BASE}/health`);
    return handleResponse<HealthStatus>(res);
  },

  async uploadDocument(file: File, docType: 'job_description' | 'resume'): Promise<DocumentRecord> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('doc_type', docType);

    const res = await fetch(`${API_BASE}/documents/upload`, {
      method: 'POST',
      body: formData,
    });
    return handleResponse<DocumentRecord>(res);
  },

  async pasteDocument(text: string, docType: 'job_description' | 'resume', filename?: string): Promise<DocumentRecord> {
    const res = await fetch(`${API_BASE}/documents/paste`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        text,
        doc_type: docType,
        filename: filename || `${docType}_pasted.txt`,
      }),
    });
    return handleResponse<DocumentRecord>(res);
  },

  async analyzeJob(documentId: string): Promise<JobAnalysis> {
    const res = await fetch(`${API_BASE}/analysis/job`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ document_id: documentId }),
    });
    return handleResponse<JobAnalysis>(res);
  },

  async analyzeCandidate(documentId: string): Promise<CandidateAnalysis> {
    const res = await fetch(`${API_BASE}/analysis/candidate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ document_id: documentId }),
    });
    return handleResponse<CandidateAnalysis>(res);
  },

  async calculateJobFit(jobAnalysisId: string, candidateAnalysisId: string): Promise<JobFitAssessment> {
    const res = await fetch(`${API_BASE}/analysis/job-fit`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        job_analysis_id: jobAnalysisId,
        candidate_analysis_id: candidateAnalysisId,
      }),
    });
    return handleResponse<JobFitAssessment>(res);
  },

  async startInterview(
    jobAnalysisId: string,
    candidateAnalysisId: string,
    jobFitId: string,
    interviewLevel: 'screening' | 'competency' | 'deep_dive',
    maxQuestions: number = 6
  ): Promise<{
    session: InterviewSession;
    current_turn: InterviewTurn;
    role_title: string;
    candidate_name: string;
  }> {
    const res = await fetch(`${API_BASE}/interview/start`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        job_analysis_id: jobAnalysisId,
        candidate_analysis_id: candidateAnalysisId,
        job_fit_id: jobFitId,
        interview_level: interviewLevel,
        max_questions: maxQuestions,
      }),
    });
    return handleResponse(res);
  },

  async getSessionDetail(sessionId: string): Promise<{
    session: InterviewSession;
    turns: InterviewTurn[];
    current_turn: InterviewTurn | null;
    role_title?: string;
    candidate_name?: string;
  }> {
    const res = await fetch(`${API_BASE}/interview/${sessionId}`);
    return handleResponse(res);
  },

  async submitAnswer(
    sessionId: string,
    answerText: string,
    transcript: string = '',
    audioUsed: boolean = false
  ): Promise<{
    session: InterviewSession;
    evaluated_turn: InterviewTurn;
    next_turn: InterviewTurn | null;
    is_completed: boolean;
    all_turns: InterviewTurn[];
  }> {
    const res = await fetch(`${API_BASE}/interview/${sessionId}/answer`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        answer_text: answerText,
        transcript,
        audio_used: audioUsed,
      }),
    });
    return handleResponse(res);
  },

  async finishInterviewEarly(sessionId: string): Promise<InterviewSession> {
    const res = await fetch(`${API_BASE}/interview/${sessionId}/finish`, {
      method: 'POST',
    });
    return handleResponse<InterviewSession>(res);
  },

  async getReport(sessionId: string): Promise<PerformanceReport> {
    const res = await fetch(`${API_BASE}/reports/${sessionId}`);
    return handleResponse<PerformanceReport>(res);
  },

  async exportReportMarkdown(sessionId: string): Promise<string> {
    const res = await fetch(`${API_BASE}/reports/${sessionId}/export?format=markdown`);
    if (!res.ok) {
      throw new Error('Failed to export markdown report.');
    }
    return res.text();
  },

  async listRecentSessions(): Promise<any[]> {
    const res = await fetch(`${API_BASE}/interview/sessions/recent`);
    return handleResponse<any[]>(res);
  },
};
