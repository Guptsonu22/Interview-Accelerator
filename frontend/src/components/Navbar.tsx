import React from 'react';
import { ScreenView, HealthStatus } from '../types';
import { Sparkles, FileText, CheckCircle2, Mic, Award, RotateCcw } from 'lucide-react';

interface NavbarProps {
  currentView: ScreenView;
  onNavigate: (view: ScreenView) => void;
  health: HealthStatus | null;
  onReset: () => void;
  canNavigateAnalysis: boolean;
  canNavigateInterview: boolean;
  canNavigateReport: boolean;
}

export const Navbar: React.FC<NavbarProps> = ({
  currentView,
  onNavigate,
  health,
  onReset,
  canNavigateAnalysis,
  canNavigateInterview,
  canNavigateReport,
}) => {
  return (
    <header className="navbar">
      <div className="nav-brand" onClick={() => onNavigate('intake')}>
        <div className="brand-icon">
          <Sparkles size={20} color="#fff" />
        </div>
        <div>
          <span className="brand-name">Interview Accelerator</span>
          <span className="brand-tag" style={{ marginLeft: 8 }}>EDXSO Assignment 3</span>
        </div>
      </div>

      <nav style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
        <button
          className={`btn ${currentView === 'intake' ? 'btn-primary' : 'btn-secondary'}`}
          style={{ padding: '6px 14px', fontSize: '0.85rem' }}
          onClick={() => onNavigate('intake')}
        >
          <FileText size={15} />
          <span>1. Intake</span>
        </button>

        <button
          className={`btn ${currentView === 'analysis' ? 'btn-primary' : 'btn-secondary'}`}
          style={{ padding: '6px 14px', fontSize: '0.85rem' }}
          disabled={!canNavigateAnalysis}
          onClick={() => onNavigate('analysis')}
        >
          <CheckCircle2 size={15} />
          <span>2. Job Fit</span>
        </button>

        <button
          className={`btn ${currentView === 'interview' ? 'btn-primary' : 'btn-secondary'}`}
          style={{ padding: '6px 14px', fontSize: '0.85rem' }}
          disabled={!canNavigateInterview}
          onClick={() => onNavigate('interview')}
        >
          <Mic size={15} />
          <span>3. Interview</span>
        </button>

        <button
          className={`btn ${currentView === 'report' ? 'btn-primary' : 'btn-secondary'}`}
          style={{ padding: '6px 14px', fontSize: '0.85rem' }}
          disabled={!canNavigateReport}
          onClick={() => onNavigate('report')}
        >
          <Award size={15} />
          <span>4. Report</span>
        </button>
      </nav>

      <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
        {health?.llm_provider && (
          <span
            className={`badge ${health.llm_provider.is_demo_mode ? 'badge-warning' : 'badge-success'}`}
            title={health.llm_provider.name}
          >
            ● {health.llm_provider.is_demo_mode ? 'Demo AI (Offline)' : health.llm_provider.name}
          </span>
        )}

        <button
          className="btn btn-secondary"
          style={{ padding: '6px 12px', fontSize: '0.825rem' }}
          onClick={onReset}
          title="Start fresh intake"
        >
          <RotateCcw size={14} />
          <span>Reset</span>
        </button>
      </div>
    </header>
  );
};
