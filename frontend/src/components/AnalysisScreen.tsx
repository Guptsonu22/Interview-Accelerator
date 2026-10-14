import React, { useState } from 'react';
import type {
  JobAnalysis,
  CandidateAnalysis,
  JobFitAssessment,
  InterviewSession,
  InterviewTurn
} from '../types';
import { api } from '../services/api';
import {
  CheckCircle2,
  AlertTriangle,
  XCircle,
  Briefcase,
  Layers,
  ArrowRight
} from 'lucide-react';

interface AnalysisScreenProps {
  jobAnalysis: JobAnalysis;
  candidateAnalysis: CandidateAnalysis;
  jobFit: JobFitAssessment;
  onStartInterview: (
    session: InterviewSession,
    currentTurn: InterviewTurn,
    roleTitle: string,
    candidateName: string
  ) => void;
}

export const AnalysisScreen: React.FC<AnalysisScreenProps> = ({
  jobAnalysis,
  candidateAnalysis,
  jobFit,
  onStartInterview,
}) => {
  const [selectedLevel, setSelectedLevel] = useState<'screening' | 'competency' | 'deep_dive'>('screening');
  const [maxQuestions, setMaxQuestions] = useState<number>(6);
  const [isStarting, setIsStarting] = useState<boolean>(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const handleBegin = async () => {
    setIsStarting(true);
    setErrorMsg(null);
    try {
      const result = await api.startInterview(
        jobAnalysis.id,
        candidateAnalysis.id,
        jobFit.id,
        selectedLevel,
        maxQuestions
      );
      onStartInterview(
        result.session,
        result.current_turn,
        result.role_title,
        result.candidate_name
      );
    } catch (err: any) {
      setErrorMsg(err.message || 'Failed to start interview session.');
    } finally {
      setIsStarting(false);
    }
  };

  return (
    <div className="animate-fade-in">
      {/* Header Banner */}
      <section className="glass-panel" style={{ padding: 28, marginBottom: 24 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: 16 }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}>
              <span className="badge badge-primary">{jobAnalysis.company_name}</span>
              <span className="badge badge-success">{jobAnalysis.experience_level}</span>
            </div>
            <h1 style={{ fontSize: '2rem', fontWeight: 700, marginBottom: 6 }}>
              {jobAnalysis.role_title}
            </h1>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.95rem' }}>
              Candidate: <strong style={{ color: '#fff' }}>{candidateAnalysis.candidate_name}</strong> · Education: {jobAnalysis.education_requirements}
            </p>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: 20 }}>
            {/* Explainable Radial Score */}
            <div style={{ textAlign: 'center' }}>
              <div
                className="score-radial"
                style={{ '--score-pct': jobFit.overall_score } as React.CSSProperties}
              >
                <div className="score-radial-inner">
                  <span className="score-radial-num">{jobFit.overall_score}%</span>
                  <span className="score-radial-label">Job Fit</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {errorMsg && (
        <div style={{ background: 'rgba(239, 68, 68, 0.12)', border: '1px solid rgba(239, 68, 68, 0.3)', borderRadius: 12, padding: 14, marginBottom: 20, color: '#fca5a5' }}>
          {errorMsg}
        </div>
      )}

      {/* 5-Dimension Breakdown & Methodology */}
      <div className="grid-2" style={{ marginBottom: 24 }}>
        <div className="glass-panel" style={{ padding: 24 }}>
          <h2 style={{ fontSize: '1.15rem', fontWeight: 600, marginBottom: 14, display: 'flex', alignItems: 'center', gap: 8 }}>
            <Layers size={18} color="#818cf8" />
            <span>Deterministic Scoring Methodology</span>
          </h2>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: 16 }}>
            The Job Fit score evaluates grounded document evidence across 5 weighted dimensions. It does not measure interview verbal delivery or guarantee hiring.
          </p>

          <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', marginBottom: 4 }}>
                <span>Required Skills (35%)</span>
                <strong>{jobFit.required_skills_score}%</strong>
              </div>
              <div style={{ height: 6, background: 'rgba(255, 255, 255, 0.08)', borderRadius: 3, overflow: 'hidden' }}>
                <div style={{ width: `${jobFit.required_skills_score}%`, height: '100%', background: '#6366f1', borderRadius: 3 }} />
              </div>
            </div>

            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', marginBottom: 4 }}>
                <span>Preferred Skills (15%)</span>
                <strong>{jobFit.preferred_skills_score}%</strong>
              </div>
              <div style={{ height: 6, background: 'rgba(255, 255, 255, 0.08)', borderRadius: 3, overflow: 'hidden' }}>
                <div style={{ width: `${jobFit.preferred_skills_score}%`, height: '100%', background: '#8b5cf6', borderRadius: 3 }} />
              </div>
            </div>

            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', marginBottom: 4 }}>
                <span>Project & Practical Evidence (20%)</span>
                <strong>{jobFit.project_evidence_score}%</strong>
              </div>
              <div style={{ height: 6, background: 'rgba(255, 255, 255, 0.08)', borderRadius: 3, overflow: 'hidden' }}>
                <div style={{ width: `${jobFit.project_evidence_score}%`, height: '100%', background: '#06b6d4', borderRadius: 3 }} />
              </div>
            </div>

            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', marginBottom: 4 }}>
                <span>Responsibilities Alignment (15%)</span>
                <strong>{jobFit.responsibility_score}%</strong>
              </div>
              <div style={{ height: 6, background: 'rgba(255, 255, 255, 0.08)', borderRadius: 3, overflow: 'hidden' }}>
                <div style={{ width: `${jobFit.responsibility_score}%`, height: '100%', background: '#10b981', borderRadius: 3 }} />
              </div>
            </div>

            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', marginBottom: 4 }}>
                <span>Experience & Qualifications (15%)</span>
                <strong>{jobFit.experience_score}%</strong>
              </div>
              <div style={{ height: 6, background: 'rgba(255, 255, 255, 0.08)', borderRadius: 3, overflow: 'hidden' }}>
                <div style={{ width: `${jobFit.experience_score}%`, height: '100%', background: '#f59e0b', borderRadius: 3 }} />
              </div>
            </div>
          </div>
        </div>

        {/* Reasons & Extracted Candidate Claims */}
        <div className="glass-panel" style={{ padding: 24 }}>
          <h2 style={{ fontSize: '1.15rem', fontWeight: 600, marginBottom: 14, display: 'flex', alignItems: 'center', gap: 8 }}>
            <Briefcase size={18} color="#c084fc" />
            <span>Key Match Observations</span>
          </h2>
          <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: 10, marginBottom: 16 }}>
            {jobFit.key_reasons.map((r, i) => (
              <li key={i} style={{ display: 'flex', gap: 10, fontSize: '0.875rem', color: 'var(--text-muted)' }}>
                <span style={{ color: '#818cf8', fontWeight: 700 }}>•</span>
                <span>{r}</span>
              </li>
            ))}
          </ul>

          <h3 style={{ fontSize: '0.9rem', fontWeight: 600, color: '#e2e8f0', marginBottom: 8 }}>
            Grounded Resume Claims (Targeted For Verification):
          </h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
            {candidateAnalysis.quantified_claims.slice(0, 3).map((claim, idx) => (
              <div key={idx} style={{ padding: '8px 12px', background: 'rgba(255, 255, 255, 0.03)', borderRadius: 8, fontSize: '0.8rem', color: '#cbd5e1' }}>
                "{claim}"
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Categorized Requirements Grid */}
      <section className="glass-panel" style={{ padding: 24, marginBottom: 28 }}>
        <h2 style={{ fontSize: '1.15rem', fontWeight: 600, marginBottom: 16 }}>
          Documented Requirements vs Candidate Evidence
        </h2>

        <div className="grid-3">
          {/* Explicitly Demonstrated */}
          <div style={{ background: 'rgba(16, 185, 129, 0.05)', border: '1px solid rgba(16, 185, 129, 0.2)', borderRadius: 12, padding: 16 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 10, color: '#34d399' }}>
              <CheckCircle2 size={18} />
              <h3 style={{ fontSize: '0.95rem', fontWeight: 600 }}>Demonstrated ({jobFit.matched_skills.length})</h3>
            </div>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
              {jobFit.matched_skills.map((s, idx) => (
                <span key={idx} className="badge badge-success" title={s.evidence}>
                  {s.skill}
                </span>
              ))}
              {jobFit.matched_skills.length === 0 && (
                <span style={{ fontSize: '0.8rem', color: 'var(--text-dim)' }}>None evidenced.</span>
              )}
            </div>
          </div>

          {/* Partially Evidenced */}
          <div style={{ background: 'rgba(245, 158, 11, 0.05)', border: '1px solid rgba(245, 158, 11, 0.2)', borderRadius: 12, padding: 16 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 10, color: '#fbbf24' }}>
              <AlertTriangle size={18} />
              <h3 style={{ fontSize: '0.95rem', fontWeight: 600 }}>Partially Evidenced ({jobFit.partial_skills.length})</h3>
            </div>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
              {jobFit.partial_skills.map((s, idx) => (
                <span key={idx} className="badge badge-warning" title={s.evidence}>
                  {s.skill}
                </span>
              ))}
              {jobFit.partial_skills.length === 0 && (
                <span style={{ fontSize: '0.8rem', color: 'var(--text-dim)' }}>No partial skills.</span>
              )}
            </div>
          </div>

          {/* Missing Evidence */}
          <div style={{ background: 'rgba(239, 68, 68, 0.05)', border: '1px solid rgba(239, 68, 68, 0.2)', borderRadius: 12, padding: 16 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 10, color: '#f87171' }}>
              <XCircle size={18} />
              <h3 style={{ fontSize: '0.95rem', fontWeight: 600 }}>Not Evidenced in Resume ({jobFit.missing_skills.length})</h3>
            </div>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
              {jobFit.missing_skills.map((s, idx) => (
                <span key={idx} className="badge badge-danger" title={s.evidence}>
                  {s.skill}
                </span>
              ))}
              {jobFit.missing_skills.length === 0 && (
                <span style={{ fontSize: '0.8rem', color: 'var(--text-dim)' }}>All requirements evidenced.</span>
              )}
            </div>
          </div>
        </div>
      </section>

      {/* Level Selection & Start CTA */}
      <section className="glass-panel" style={{ padding: 28, textAlign: 'center' }}>
        <h2 style={{ fontSize: '1.35rem', fontWeight: 700, marginBottom: 8 }}>
          Select Adaptive Interview Level
        </h2>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.95rem', marginBottom: 24, maxWidth: 640, margin: '0 auto 24px auto' }}>
          Each level dynamically generates questions tailored to the candidate's exact resume and target role.
        </p>

        <div className="grid-3" style={{ marginBottom: 24 }}>
          {/* Level 1: Screening */}
          <div
            onClick={() => setSelectedLevel('screening')}
            style={{
              padding: 20,
              borderRadius: 14,
              border: `2px solid ${selectedLevel === 'screening' ? '#6366f1' : 'var(--border-subtle)'}`,
              background: selectedLevel === 'screening' ? 'rgba(99, 102, 241, 0.1)' : 'rgba(255, 255, 255, 0.02)',
              cursor: 'pointer',
              textAlign: 'left',
              transition: 'all 0.2s ease',
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
              <span className="badge badge-primary">Level 1</span>
              {selectedLevel === 'screening' && <CheckCircle2 size={18} color="#818cf8" />}
            </div>
            <h3 style={{ fontSize: '1.1rem', fontWeight: 600, marginBottom: 6 }}>Screening Interview</h3>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
              Assesses motivation, career goals, project walkthrough, communication, and initial role fit.
            </p>
          </div>

          {/* Level 2: Competency */}
          <div
            onClick={() => setSelectedLevel('competency')}
            style={{
              padding: 20,
              borderRadius: 14,
              border: `2px solid ${selectedLevel === 'competency' ? '#8b5cf6' : 'var(--border-subtle)'}`,
              background: selectedLevel === 'competency' ? 'rgba(139, 92, 246, 0.1)' : 'rgba(255, 255, 255, 0.02)',
              cursor: 'pointer',
              textAlign: 'left',
              transition: 'all 0.2s ease',
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
              <span className="badge badge-primary">Level 2</span>
              {selectedLevel === 'competency' && <CheckCircle2 size={18} color="#c084fc" />}
            </div>
            <h3 style={{ fontSize: '1.1rem', fontWeight: 600, marginBottom: 6 }}>Competency Interview</h3>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
              Assesses technical fundamentals, role-specific practical application, architecture, and engineering trade-offs.
            </p>
          </div>

          {/* Level 3: Deep-Dive */}
          <div
            onClick={() => setSelectedLevel('deep_dive')}
            style={{
              padding: 20,
              borderRadius: 14,
              border: `2px solid ${selectedLevel === 'deep_dive' ? '#06b6d4' : 'var(--border-subtle)'}`,
              background: selectedLevel === 'deep_dive' ? 'rgba(6, 182, 212, 0.1)' : 'rgba(255, 255, 255, 0.02)',
              cursor: 'pointer',
              textAlign: 'left',
              transition: 'all 0.2s ease',
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
              <span className="badge badge-primary">Level 3</span>
              {selectedLevel === 'deep_dive' && <CheckCircle2 size={18} color="#22d3ee" />}
            </div>
            <h3 style={{ fontSize: '1.1rem', fontWeight: 600, marginBottom: 6 }}>Deep-Dive Interview</h3>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
              Assesses technical depth, edge cases, failure handling, security, and verifies resume metrics.
            </p>
          </div>
        </div>

        <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', gap: 16, marginBottom: 20 }}>
          <span style={{ fontSize: '0.9rem', color: 'var(--text-muted)' }}>Target Session Length:</span>
          <select
            value={maxQuestions}
            onChange={(e) => setMaxQuestions(Number(e.target.value))}
            style={{
              background: 'rgba(10, 15, 26, 0.8)',
              border: '1px solid var(--border-subtle)',
              borderRadius: 8,
              color: '#fff',
              padding: '6px 12px',
              fontFamily: 'var(--font-body)',
              fontSize: '0.9rem',
            }}
          >
            <option value={4}>4 Questions (Quick Drill)</option>
            <option value={6}>6 Questions (Standard Round)</option>
            <option value={8}>8 Questions (Comprehensive)</option>
          </select>
        </div>

        <button
          className="btn btn-primary"
          style={{ padding: '14px 40px', fontSize: '1.1rem', minWidth: 260 }}
          disabled={isStarting}
          onClick={handleBegin}
        >
          {isStarting ? (
            <span>Starting Interview...</span>
          ) : (
            <>
              <span>Begin {selectedLevel.replace('_', ' ').toUpperCase()} Interview</span>
              <ArrowRight size={18} />
            </>
          )}
        </button>
      </section>
    </div>
  );
};
