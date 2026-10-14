import React, { useState } from 'react';
import type { PerformanceReport } from '../types';
import { api } from '../services/api';
import {
  CheckCircle2,
  AlertTriangle,
  Download,
  Printer,
  RotateCcw,
  BookOpen,
  ChevronDown,
  ChevronUp,
  TrendingUp
} from 'lucide-react';

interface ReportScreenProps {
  report: PerformanceReport;
  onReset: () => void;
}

export const ReportScreen: React.FC<ReportScreenProps> = ({ report, onReset }) => {
  const [openTurnIndex, setOpenTurnIndex] = useState<number | null>(0);
  const [isExporting, setIsExporting] = useState<boolean>(false);

  const handleDownloadMarkdown = async () => {
    setIsExporting(true);
    try {
      const mdContent = await api.exportReportMarkdown(report.session_id);
      const blob = new Blob([mdContent], { type: 'text/markdown;charset=utf-8;' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `interview_report_${report.session_id.slice(0, 8)}.md`);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } catch (err: any) {
      alert(err.message || 'Failed to download report.');
    } finally {
      setIsExporting(false);
    }
  };

  const handlePrint = () => {
    window.print();
  };

  const getReadinessBadgeClass = (category: string) => {
    switch (category) {
      case 'STRONG CANDIDATE':
        return 'badge-success';
      case 'INTERVIEW READY':
        return 'badge-primary';
      case 'NEEDS PREPARATION':
        return 'badge-warning';
      default:
        return 'badge-danger';
    }
  };

  const competencies = [
    { label: 'Role Fit', score: report.role_fit_score, desc: 'Alignment with target role expectations' },
    { label: 'Technical Knowledge', score: report.technical_knowledge_score, desc: 'Accuracy and engineering fundamentals' },
    { label: 'Problem Solving', score: report.problem_solving_score, desc: 'Diagnostics, method, and solution framing' },
    { label: 'Communication', score: report.communication_score, desc: 'Clarity, structure, and conciseness' },
    { label: 'Confidence & Delivery', score: report.confidence_score, desc: 'Objective answer completeness and low hesitation' },
    { label: 'Depth of Understanding', score: report.depth_score, desc: 'Edge cases, failure handling, and trade-offs' },
    { label: 'Behavioral Fit', score: report.behavioral_fit_score, desc: 'Ownership, adaptability, and collaboration' },
  ];

  return (
    <div className="animate-fade-in" style={{ paddingBottom: 60 }}>
      {/* Top Banner */}
      <section className="glass-panel" style={{ padding: 32, marginBottom: 24 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: 20 }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 8 }}>
              <span className={`badge ${getReadinessBadgeClass(report.readiness_category)}`} style={{ fontSize: '0.85rem', padding: '6px 14px' }}>
                ● {report.readiness_category}
              </span>
              <span className="badge badge-primary">Comprehensive Report</span>
            </div>
            <h1 style={{ fontSize: '2.25rem', fontWeight: 700, marginBottom: 6 }}>
              Interview Readiness Assessment
            </h1>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.95rem' }}>
              Target Role: <strong style={{ color: '#fff' }}>{report.role_title || 'Software Role'}</strong> · Candidate: <strong style={{ color: '#fff' }}>{report.candidate_name || 'Candidate'}</strong>
            </p>
          </div>

          {/* Overall Score Radial */}
          <div style={{ display: 'flex', alignItems: 'center', gap: 24 }}>
            <div
              className="score-radial"
              style={{ '--score-pct': report.overall_score } as React.CSSProperties}
            >
              <div className="score-radial-inner">
                <span className="score-radial-num">{report.overall_score}</span>
                <span className="score-radial-label">Score / 100</span>
              </div>
            </div>
          </div>
        </div>

        {/* Executive Rationale Alert */}
        <div style={{ marginTop: 20, padding: 16, background: 'rgba(99, 102, 241, 0.08)', border: '1px solid rgba(99, 102, 241, 0.25)', borderRadius: 12 }}>
          <strong style={{ color: '#a5b4fc', fontSize: '0.9rem', display: 'block', marginBottom: 4 }}>
            Evaluation Verdict & Rationale:
          </strong>
          <p style={{ color: '#e2e8f0', fontSize: '0.925rem', lineHeight: 1.6 }}>
            {report.readiness_rationale}
          </p>
        </div>
      </section>

      {/* Comparison: Job Fit vs Interview Performance */}
      <section className="glass-panel" style={{ padding: 24, marginBottom: 24, border: '1px solid rgba(6, 182, 212, 0.25)', background: 'rgba(6, 182, 212, 0.03)' }}>
        <h2 style={{ fontSize: '1.1rem', fontWeight: 600, display: 'flex', alignItems: 'center', gap: 8, marginBottom: 12, color: '#22d3ee' }}>
          <TrendingUp size={20} />
          <span>Job Fit vs. Interview Performance Comparison</span>
        </h2>
        <div className="grid-2">
          <div>
            <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Resume-to-Job Fit (What is on paper):</span>
            <div style={{ fontSize: '1.5rem', fontWeight: 700, color: '#6366f1', marginTop: 4 }}>
              {report.job_fit_score !== undefined ? `${report.job_fit_score}%` : 'Assessed'}
            </div>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-dim)', marginTop: 4 }}>
              Static alignment between job requirements and resume bullet keywords.
            </p>
          </div>
          <div>
            <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Interview Performance (What you defended live):</span>
            <div style={{ fontSize: '1.5rem', fontWeight: 700, color: '#10b981', marginTop: 4 }}>
              {report.overall_score}%
            </div>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-dim)', marginTop: 4 }}>
              Live verbal reasoning, architectural depth, trade-offs, and failure handling.
            </p>
          </div>
        </div>
      </section>

      {/* Seven Core Competency Scores Grid */}
      <section className="glass-panel" style={{ padding: 24, marginBottom: 24 }}>
        <h2 style={{ fontSize: '1.15rem', fontWeight: 600, marginBottom: 16 }}>
          Seven Core Evaluated Competencies
        </h2>
        <div className="grid-2" style={{ gap: 18 }}>
          {competencies.map((c, i) => (
            <div key={i} style={{ padding: 14, background: 'rgba(10, 15, 26, 0.5)', borderRadius: 10, border: '1px solid var(--border-subtle)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 }}>
                <span style={{ fontWeight: 600, fontSize: '0.9rem' }}>{c.label}</span>
                <strong style={{ fontSize: '1rem', color: c.score >= 75 ? '#34d399' : c.score >= 60 ? '#818cf8' : '#fbbf24' }}>
                  {c.score}/100
                </strong>
              </div>
              <div style={{ height: 6, background: 'rgba(255, 255, 255, 0.08)', borderRadius: 3, overflow: 'hidden', marginBottom: 6 }}>
                <div
                  style={{
                    width: `${c.score}%`,
                    height: '100%',
                    background: c.score >= 75 ? '#10b981' : c.score >= 60 ? '#6366f1' : '#f59e0b',
                    borderRadius: 3,
                  }}
                />
              </div>
              <p style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }}>{c.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Evidenced Strengths & Weaknesses */}
      <div className="grid-2" style={{ marginBottom: 24 }}>
        {/* Strengths */}
        <div className="glass-panel" style={{ padding: 24 }}>
          <h2 style={{ fontSize: '1.15rem', fontWeight: 600, color: '#34d399', display: 'flex', alignItems: 'center', gap: 8, marginBottom: 14 }}>
            <CheckCircle2 size={20} />
            <span>Evidenced Strengths</span>
          </h2>
          <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: 12 }}>
            {report.demonstrated_strengths.map((str, idx) => (
              <li key={idx} style={{ padding: 12, background: 'rgba(16, 185, 129, 0.05)', borderRadius: 8, border: '1px solid rgba(16, 185, 129, 0.2)', fontSize: '0.875rem', color: '#e2e8f0' }}>
                {str}
              </li>
            ))}
          </ul>
        </div>

        {/* Weaknesses */}
        <div className="glass-panel" style={{ padding: 24 }}>
          <h2 style={{ fontSize: '1.15rem', fontWeight: 600, color: '#fbbf24', display: 'flex', alignItems: 'center', gap: 8, marginBottom: 14 }}>
            <AlertTriangle size={20} />
            <span>Evidenced Knowledge & Reasoning Gaps</span>
          </h2>
          <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: 12 }}>
            {report.evidenced_weaknesses.map((wk, idx) => (
              <li key={idx} style={{ padding: 12, background: 'rgba(245, 158, 11, 0.05)', borderRadius: 8, border: '1px solid rgba(245, 158, 11, 0.2)', fontSize: '0.875rem', color: '#e2e8f0' }}>
                {wk}
              </li>
            ))}
          </ul>
        </div>
      </div>

      {/* Prioritized Preparation Roadmap */}
      <section className="glass-panel" style={{ padding: 24, marginBottom: 24 }}>
        <h2 style={{ fontSize: '1.25rem', fontWeight: 700, marginBottom: 16, display: 'flex', alignItems: 'center', gap: 8 }}>
          <BookOpen size={20} color="#818cf8" />
          <span>Prioritized Preparation Roadmap</span>
        </h2>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          {report.prioritized_prep_plan.map((item, idx) => (
            <div key={idx} style={{ padding: 18, background: 'rgba(10, 15, 26, 0.7)', borderRadius: 12, border: '1px solid var(--border-subtle)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
                <span className="badge badge-primary">Priority {item.priority}</span>
                <strong style={{ fontSize: '1rem', color: '#fff' }}>{item.topic}</strong>
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 12, fontSize: '0.85rem', marginTop: 10 }}>
                <div>
                  <span style={{ color: 'var(--text-dim)', display: 'block' }}>Why It Matters:</span>
                  <p style={{ color: '#cbd5e1' }}>{item.why_it_matters}</p>
                </div>
                <div>
                  <span style={{ color: 'var(--text-dim)', display: 'block' }}>What To Study:</span>
                  <p style={{ color: '#cbd5e1' }}>{item.what_to_study}</p>
                </div>
                <div>
                  <span style={{ color: 'var(--text-dim)', display: 'block' }}>Practical Exercise:</span>
                  <p style={{ color: '#cbd5e1' }}>{item.practical_exercise}</p>
                </div>
                <div>
                  <span style={{ color: 'var(--text-dim)', display: 'block' }}>Completion Criteria:</span>
                  <p style={{ color: '#34d399' }}>{item.completion_criteria}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Question-Level Detailed Rubric Feedback */}
      <section className="glass-panel" style={{ padding: 24, marginBottom: 30 }}>
        <h2 style={{ fontSize: '1.25rem', fontWeight: 700, marginBottom: 16 }}>
          Question-by-Question Rubric Breakdown
        </h2>

        <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
          {report.question_feedback_list.map((qf, i) => {
            const isOpen = openTurnIndex === i;
            return (
              <div key={i} style={{ border: '1px solid var(--border-subtle)', borderRadius: 12, overflow: 'hidden', background: 'rgba(10, 15, 26, 0.6)' }}>
                <div
                  onClick={() => setOpenTurnIndex(isOpen ? null : i)}
                  style={{
                    padding: '16px 20px',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    cursor: 'pointer',
                    background: isOpen ? 'rgba(99, 102, 241, 0.08)' : 'transparent',
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                    <span className="badge badge-secondary">Q{qf.turn_index + 1}</span>
                    <span style={{ fontWeight: 600, fontSize: '0.95rem' }}>{qf.question}</span>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
                    <span className="badge badge-primary">Score: {qf.score}/100</span>
                    {isOpen ? <ChevronUp size={18} /> : <ChevronDown size={18} />}
                  </div>
                </div>

                {isOpen && (
                  <div style={{ padding: '20px 24px', borderTop: '1px solid var(--border-subtle)', display: 'flex', flexDirection: 'column', gap: 14, fontSize: '0.875rem' }}>
                    <div style={{ padding: 12, background: 'rgba(255, 255, 255, 0.03)', borderRadius: 8 }}>
                      <span style={{ color: 'var(--text-dim)', display: 'block', marginBottom: 4 }}>Candidate Answer:</span>
                      <p style={{ fontStyle: 'italic', color: '#e2e8f0' }}>"{qf.candidate_answer}"</p>
                    </div>

                    <div className="grid-2" style={{ gap: 14 }}>
                      <div style={{ background: 'rgba(16, 185, 129, 0.05)', padding: 12, borderRadius: 8, border: '1px solid rgba(16, 185, 129, 0.2)' }}>
                        <strong style={{ color: '#34d399', display: 'block', marginBottom: 4 }}>What Was Good:</strong>
                        <p style={{ color: '#e2e8f0' }}>{qf.feedback_good}</p>
                      </div>
                      <div style={{ background: 'rgba(245, 158, 11, 0.05)', padding: 12, borderRadius: 8, border: '1px solid rgba(245, 158, 11, 0.2)' }}>
                        <strong style={{ color: '#fbbf24', display: 'block', marginBottom: 4 }}>What Could Be Improved:</strong>
                        <p style={{ color: '#e2e8f0' }}>{qf.feedback_improve}</p>
                      </div>
                    </div>

                    {qf.missing_concepts && qf.missing_concepts.length > 0 && (
                      <div style={{ padding: 12, background: 'rgba(239, 68, 68, 0.05)', borderRadius: 8, border: '1px solid rgba(239, 68, 68, 0.2)' }}>
                        <strong style={{ color: '#f87171', display: 'block', marginBottom: 4 }}>Key Missing Concepts:</strong>
                        <p style={{ color: '#e2e8f0' }}>{qf.missing_concepts.join(', ')}</p>
                      </div>
                    )}

                    <div style={{ padding: 14, background: 'rgba(99, 102, 241, 0.05)', borderRadius: 8, border: '1px solid rgba(99, 102, 241, 0.2)' }}>
                      <strong style={{ color: '#818cf8', display: 'block', marginBottom: 4 }}>Ideal Answer Direction:</strong>
                      <p style={{ color: '#e2e8f0', lineHeight: 1.6 }}>{qf.ideal_answer_direction}</p>
                    </div>

                    <div style={{ padding: 12, background: 'rgba(255, 255, 255, 0.02)', borderRadius: 8 }}>
                      <strong style={{ color: '#38bdf8', display: 'block', marginBottom: 4 }}>Practice Recommendation:</strong>
                      <p style={{ color: '#cbd5e1' }}>{qf.follow_up_recommendation}</p>
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </section>

      {/* Export & Navigation Controls */}
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', gap: 16, flexWrap: 'wrap' }}>
        <button
          className="btn btn-primary"
          style={{ padding: '12px 28px' }}
          onClick={handleDownloadMarkdown}
          disabled={isExporting}
        >
          <Download size={16} />
          <span>{isExporting ? 'Exporting...' : 'Download Markdown Report'}</span>
        </button>

        <button
          className="btn btn-secondary"
          style={{ padding: '12px 24px' }}
          onClick={handlePrint}
        >
          <Printer size={16} />
          <span>Print / PDF View</span>
        </button>

        <button
          className="btn btn-secondary"
          style={{ padding: '12px 24px' }}
          onClick={onReset}
        >
          <RotateCcw size={16} />
          <span>Prepare for Another Role</span>
        </button>
      </div>
    </div>
  );
};
