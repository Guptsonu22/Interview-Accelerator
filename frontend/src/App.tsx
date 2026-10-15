import React, { useState, useEffect } from 'react';
import type {
  ScreenView,
  DocumentRecord,
  JobAnalysis,
  CandidateAnalysis,
  JobFitAssessment,
  InterviewSession,
  InterviewTurn,
  PerformanceReport,
  HealthStatus
} from './types';
import { api } from './services/api';
import { Navbar } from './components/Navbar';
import { IntakeScreen } from './components/IntakeScreen';
import { AnalysisScreen } from './components/AnalysisScreen';
import { InterviewRoomScreen } from './components/InterviewRoomScreen';
import { ReportScreen } from './components/ReportScreen';

export const App: React.FC = () => {
  const [currentView, setCurrentView] = useState<ScreenView>('intake');
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [recentSessions, setRecentSessions] = useState<any[]>([]);

  // State
  const [jobAnalysis, setJobAnalysis] = useState<JobAnalysis | null>(null);
  const [candidateAnalysis, setCandidateAnalysis] = useState<CandidateAnalysis | null>(null);
  const [jobFit, setJobFit] = useState<JobFitAssessment | null>(null);

  const [session, setSession] = useState<InterviewSession | null>(null);
  const [currentTurn, setCurrentTurn] = useState<InterviewTurn | null>(null);
  const [roleTitle, setRoleTitle] = useState<string>('');
  const [candidateName, setCandidateName] = useState<string>('');
  const [report, setReport] = useState<PerformanceReport | null>(null);

  const loadRecentSessions = () => {
    api.listRecentSessions()
      .then((s) => setRecentSessions(s))
      .catch((err) => console.warn('Could not load recent sessions:', err));
  };

  const handleResumeSession = async (sessionId: string) => {
    try {
      const detail = await api.getSessionDetail(sessionId);
      setSession(detail.session);
      setRoleTitle(detail.role_title || 'Software Role');
      setCandidateName(detail.candidate_name || 'Candidate');

      if (detail.session.status === 'completed') {
        const rep = await api.getReport(sessionId);
        setReport(rep);
        setCurrentView('report');
      } else {
        if (detail.current_turn) {
          setCurrentTurn(detail.current_turn);
        }
        setCurrentView('interview');
      }
    } catch (err) {
      console.warn('Could not restore session:', err);
      localStorage.removeItem('interview_accelerator_active_session');
    }
  };

  // Initial load: health check & recent sessions
  useEffect(() => {
    api.getHealth()
      .then((h) => setHealth(h))
      .catch((err) => console.warn('Health check issue:', err));

    loadRecentSessions();

    // Check localStorage for active session
    const savedSessionId = localStorage.getItem('interview_accelerator_active_session');
    if (savedSessionId) {
      handleResumeSession(savedSessionId);
    }
  }, []);

  const handleAnalysisComplete = (
    _jDoc: DocumentRecord,
    _rDoc: DocumentRecord,
    jAnalysis: JobAnalysis,
    cAnalysis: CandidateAnalysis,
    fit: JobFitAssessment
  ) => {
    setJobAnalysis(jAnalysis);
    setCandidateAnalysis(cAnalysis);
    setJobFit(fit);
    setRoleTitle(jAnalysis.role_title);
    setCandidateName(cAnalysis.candidate_name);
    setCurrentView('analysis');
  };

  const handleStartInterview = (
    newSession: InterviewSession,
    turn: InterviewTurn,
    role: string,
    candidate: string
  ) => {
    setSession(newSession);
    setCurrentTurn(turn);
    setRoleTitle(role);
    setCandidateName(candidate);
    localStorage.setItem('interview_accelerator_active_session', newSession.id);
    setCurrentView('interview');
    loadRecentSessions();
  };

  const handleFinishSession = (completedReport: PerformanceReport) => {
    setReport(completedReport);
    setCurrentView('report');
    localStorage.removeItem('interview_accelerator_active_session');
    loadRecentSessions();
  };


  const handleReset = () => {
    if (currentView === 'interview' && session?.status !== 'completed') {
      if (!window.confirm('Reset current intake? Unfinished session answers will be preserved in history.')) {
        return;
      }
    }
    localStorage.removeItem('interview_accelerator_active_session');
    setJobAnalysis(null);
    setCandidateAnalysis(null);
    setJobFit(null);
    setSession(null);
    setCurrentTurn(null);
    setReport(null);
    setCurrentView('intake');
    loadRecentSessions();
  };

  return (
    <div className="app-container">
      <Navbar
        currentView={currentView}
        onNavigate={(v) => setCurrentView(v)}
        health={health}
        onReset={handleReset}
        canNavigateAnalysis={Boolean(jobAnalysis && candidateAnalysis && jobFit)}
        canNavigateInterview={Boolean(session && currentTurn)}
        canNavigateReport={Boolean(report)}
      />

      <main>
        {currentView === 'intake' && (
          <IntakeScreen
            onAnalysisComplete={handleAnalysisComplete}
            recentSessions={recentSessions}
            onResumeSession={handleResumeSession}
          />
        )}

        {currentView === 'analysis' && jobAnalysis && candidateAnalysis && jobFit && (
          <AnalysisScreen
            jobAnalysis={jobAnalysis}
            candidateAnalysis={candidateAnalysis}
            jobFit={jobFit}
            onStartInterview={handleStartInterview}
          />
        )}

        {currentView === 'interview' && session && currentTurn && (
          <InterviewRoomScreen
            session={session}
            initialTurn={currentTurn}
            roleTitle={roleTitle}
            candidateName={candidateName}
            onFinishSession={handleFinishSession}
          />
        )}

        {currentView === 'report' && report && (
          <ReportScreen report={report} onReset={handleReset} />
        )}
      </main>
    </div>
  );
};

export default App;
