import React, { useState } from 'react';
import { Upload, FileText, CheckCircle2, ArrowRight, Clock, AlertCircle } from 'lucide-react';
import { api } from '../services/api';
import type { DocumentRecord, JobAnalysis, CandidateAnalysis, JobFitAssessment } from '../types';

interface IntakeScreenProps {
  onAnalysisComplete: (
    jobDoc: DocumentRecord,
    resumeDoc: DocumentRecord,
    jobAnalysis: JobAnalysis,
    candidateAnalysis: CandidateAnalysis,
    jobFit: JobFitAssessment
  ) => void;
  recentSessions: any[];
  onResumeSession: (sessionId: string) => void;
}

const SAMPLE_JD = `Role: Senior Full Stack AI Engineer
Company: CloudScale Dynamics
Location: San Francisco, CA / Remote

About The Role:
We are seeking a Senior Full Stack AI Engineer to spearhead our adaptive interview intelligence systems. You will architect robust, low-latency web services connecting modern frontend applications with language model reasoning engines.

Key Responsibilities:
- Design, build, and deploy production-grade full-stack features using React, TypeScript, and FastAPI.
- Implement structured prompt pipelines with strict schema validation and deterministic fallbacks.
- Design normalized relational databases (PostgreSQL/SQLite) with migration-ready models and caching.
- Build reliable audio and real-time streaming interfaces using Web Speech and WebSocket protocols.
- Mentor junior engineers, drive code review quality, and write comprehensive pytest and Playwright suites.

Required Skills & Competencies:
- 3+ years professional experience with Python, FastAPI, React, and TypeScript.
- Strong knowledge of RESTful APIs, asynchronous programming, and state management.
- Experience with relational databases, indexing, and connection pooling.
- Practical experience designing automated unit and integration tests.

Preferred Skills:
- Experience with Docker, Kubernetes, and automated CI/CD deployment pipelines.
- Knowledge of browser speech synthesis, audio recognition, and accessibility standards.
- Understanding of prompt security, injection defenses, and rate limiting.`;

const SAMPLE_RESUME = `Alex Chen
San Francisco, CA | alex.chen@example.com | github.com/alexchen-dev

Professional Summary:
Full Stack Software Engineer with 3+ years of experience engineering high-throughput web applications, REST APIs, and AI integrations using Python, FastAPI, React, and TypeScript. Proven track record of improving system latency by 35% and delivering resilient distributed features.

Technical Skills:
- Languages & Frameworks: Python, TypeScript, JavaScript, FastAPI, React, Next.js, Node.js, SQL
- Databases & Storage: PostgreSQL, SQLite, Redis, Docker
- Architecture & Tools: RESTful APIs, Git, Pytest, Docker, CI/CD, Web Speech API, TailwindCSS

Professional Experience:
Full Stack Developer | NexaFlow Technologies (2022 - Present)
- Engineered 14 high-traffic microservices using FastAPI and PostgreSQL, scaling to 45,000 daily active requests.
- Decreased API p95 query latency by 35% through query re-indexing and Redis caching layers.
- Built interactive candidate dashboards in React and TypeScript with real-time state synchronization.
- Designed comprehensive automated pytest test suites maintaining 92% coverage across core services.

Key Projects:
Adaptive Mock Interview Platform
- Designed an end-to-end AI mock interview platform featuring dynamic multi-turn questioning and deterministic rubric evaluation.
- Implemented real-time browser speech recognition and synthesis with fallback controls.
- Containerized application with Docker and automated deployment checks.

Education:
B.S. in Computer Science | California State University (2022)`;

export const IntakeScreen: React.FC<IntakeScreenProps> = ({
  onAnalysisComplete,
  recentSessions,
  onResumeSession,
}) => {
  const [jdMode, setJdMode] = useState<'paste' | 'upload'>('paste');
  const [jdText, setJdText] = useState<string>('');
  const [jdFile, setJdFile] = useState<File | null>(null);

  const [resumeMode, setResumeMode] = useState<'paste' | 'upload'>('paste');
  const [resumeText, setResumeText] = useState<string>('');
  const [resumeFile, setResumeFile] = useState<File | null>(null);

  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [loadingStep, setLoadingStep] = useState<string>('');
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const handleLoadSampleJD = () => {
    setJdMode('paste');
    setJdText(SAMPLE_JD.trim());
    setErrorMessage(null);
  };

  const handleLoadSampleResume = () => {
    setResumeMode('paste');
    setResumeText(SAMPLE_RESUME.trim());
    setErrorMessage(null);
  };

  const handleProcessIntake = async () => {
    setErrorMessage(null);

    // Validation
    if (jdMode === 'paste' && jdText.trim().length < 20) {
      setErrorMessage('Please provide a Job Description with at least 20 characters.');
      return;
    }
    if (jdMode === 'upload' && !jdFile) {
      setErrorMessage('Please select a Job Description file to upload (.pdf, .docx, or .txt).');
      return;
    }

    if (resumeMode === 'paste' && resumeText.trim().length < 20) {
      setErrorMessage('Please provide a Resume with at least 20 characters.');
      return;
    }
    if (resumeMode === 'upload' && !resumeFile) {
      setErrorMessage('Please select a Resume file to upload (.pdf, .docx, or .txt).');
      return;
    }

    setIsLoading(true);
    try {
      // 1. Process Job Description
      setLoadingStep('Extracting and validating Job Description...');
      let jobDoc: DocumentRecord;
      if (jdMode === 'upload' && jdFile) {
        jobDoc = await api.uploadDocument(jdFile, 'job_description');
      } else {
        jobDoc = await api.pasteDocument(jdText.trim(), 'job_description', 'target_job.txt');
      }

      // 2. Process Resume
      setLoadingStep('Extracting and validating Candidate Resume...');
      let resumeDoc: DocumentRecord;
      if (resumeMode === 'upload' && resumeFile) {
        resumeDoc = await api.uploadDocument(resumeFile, 'resume');
      } else {
        resumeDoc = await api.pasteDocument(resumeText.trim(), 'resume', 'candidate_resume.txt');
      }

      // 3. Grounded Job Analysis
      setLoadingStep('Extracting role requirements, competencies, and tools...');
      const jobAnalysis = await api.analyzeJob(jobDoc.id);

      // 4. Grounded Candidate Analysis
      setLoadingStep('Extracting candidate skills, projects, and verified claims...');
      const candidateAnalysis = await api.analyzeCandidate(resumeDoc.id);

      // 5. Deterministic Job Fit Calculation
      setLoadingStep('Computing explainable Job Fit score and category alignment...');
      const jobFit = await api.calculateJobFit(jobAnalysis.id, candidateAnalysis.id);

      setLoadingStep('Analysis complete!');
      onAnalysisComplete(jobDoc, resumeDoc, jobAnalysis, candidateAnalysis, jobFit);
    } catch (err: any) {
      setErrorMessage(err.message || 'An error occurred during intake processing.');
    } finally {
      setIsLoading(false);
      setLoadingStep('');
    }
  };

  return (
    <div className="animate-fade-in">
      {/* Hero Header */}
      <section style={{ textAlign: 'center', padding: '30px 0 45px 0' }}>
        <div style={{ display: 'inline-flex', alignItems: 'center', gap: 8, padding: '6px 14px', borderRadius: 9999, background: 'rgba(99, 102, 241, 0.1)', border: '1px solid rgba(99, 102, 241, 0.25)', marginBottom: 16 }}>
          <span style={{ color: '#a5b4fc', fontSize: '0.8rem', fontWeight: 600 }}>Adaptive AI Interview Preparation</span>
        </div>
        <h1 style={{ fontSize: '2.75rem', fontWeight: 700, lineHeight: 1.15, marginBottom: 16 }}>
          You are not underqualified.<br />
          <span style={{ background: 'linear-gradient(135deg, #818cf8, #c084fc)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
            You are under-evidenced.
          </span>
        </h1>
        <p style={{ maxWidth: 680, margin: '0 auto', color: 'var(--text-muted)', fontSize: '1.05rem' }}>
          Understand what an employer genuinely expects, simulate realistic screening, competency, and deep-dive rounds, and defend your actual technical claims before your interview.
        </p>
      </section>

      {/* Error Alert */}
      {errorMessage && (
        <div style={{ background: 'rgba(239, 68, 68, 0.12)', border: '1px solid rgba(239, 68, 68, 0.3)', borderRadius: 12, padding: '14px 20px', display: 'flex', alignItems: 'center', gap: 12, marginBottom: 24, color: '#fca5a5' }}>
          <AlertCircle size={20} />
          <span>{errorMessage}</span>
        </div>
      )}

      {/* Intake Cards Grid */}
      <div className="grid-2" style={{ marginBottom: 30 }}>
        {/* Card 1: Job Description */}
        <div className="glass-panel" style={{ padding: 24 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
              <div style={{ width: 32, height: 32, borderRadius: 8, background: 'rgba(99, 102, 241, 0.15)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <FileText size={18} color="#818cf8" />
              </div>
              <h2 style={{ fontSize: '1.15rem', fontWeight: 600 }}>Target Job Description</h2>
            </div>
            <button
              className="btn btn-secondary"
              style={{ fontSize: '0.75rem', padding: '4px 10px' }}
              onClick={handleLoadSampleJD}
            >
              Load Sample JD
            </button>
          </div>

          <div style={{ display: 'flex', gap: 8, marginBottom: 14 }}>
            <button
              className={`btn ${jdMode === 'paste' ? 'btn-primary' : 'btn-secondary'}`}
              style={{ padding: '4px 12px', fontSize: '0.8rem' }}
              onClick={() => setJdMode('paste')}
            >
              Paste Text
            </button>
            <button
              className={`btn ${jdMode === 'upload' ? 'btn-primary' : 'btn-secondary'}`}
              style={{ padding: '4px 12px', fontSize: '0.8rem' }}
              onClick={() => setJdMode('upload')}
            >
              Upload File
            </button>
          </div>

          {jdMode === 'paste' ? (
            <div>
              <textarea
                className="textarea-input"
                rows={10}
                placeholder="Paste the full job description here (title, requirements, tech stack, responsibilities)..."
                value={jdText}
                onChange={(e) => setJdText(e.target.value)}
              />
              <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 6, fontSize: '0.75rem', color: 'var(--text-dim)' }}>
                <span>Minimum 20 characters</span>
                <span>{jdText.length} characters</span>
              </div>
            </div>
          ) : (
            <div>
              <label className="dropzone" style={{ display: 'block' }}>
                <input
                  type="file"
                  accept=".pdf,.docx,.txt"
                  style={{ display: 'none' }}
                  onChange={(e) => {
                    if (e.target.files?.[0]) setJdFile(e.target.files[0]);
                  }}
                />
                <Upload size={32} color="#818cf8" style={{ margin: '0 auto 10px auto' }} />
                <p style={{ fontWeight: 600, fontSize: '0.9rem', marginBottom: 4 }}>
                  {jdFile ? jdFile.name : 'Click to upload or drag & drop'}
                </p>
                <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                  Supports PDF, DOCX, or TXT (Max 10MB)
                </p>
              </label>
              {jdFile && (
                <div style={{ marginTop: 10, display: 'flex', alignItems: 'center', gap: 8, fontSize: '0.85rem', color: '#34d399' }}>
                  <CheckCircle2 size={16} />
                  <span>Selected: {jdFile.name} ({(jdFile.size / 1024).toFixed(1)} KB)</span>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Card 2: Candidate Resume */}
        <div className="glass-panel" style={{ padding: 24 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
              <div style={{ width: 32, height: 32, borderRadius: 8, background: 'rgba(139, 92, 246, 0.15)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <FileText size={18} color="#c084fc" />
              </div>
              <h2 style={{ fontSize: '1.15rem', fontWeight: 600 }}>Candidate Resume</h2>
            </div>
            <button
              className="btn btn-secondary"
              style={{ fontSize: '0.75rem', padding: '4px 10px' }}
              onClick={handleLoadSampleResume}
            >
              Load Sample Resume
            </button>
          </div>

          <div style={{ display: 'flex', gap: 8, marginBottom: 14 }}>
            <button
              className={`btn ${resumeMode === 'paste' ? 'btn-primary' : 'btn-secondary'}`}
              style={{ padding: '4px 12px', fontSize: '0.8rem' }}
              onClick={() => setResumeMode('paste')}
            >
              Paste Text
            </button>
            <button
              className={`btn ${resumeMode === 'upload' ? 'btn-primary' : 'btn-secondary'}`}
              style={{ padding: '4px 12px', fontSize: '0.8rem' }}
              onClick={() => setResumeMode('upload')}
            >
              Upload File
            </button>
          </div>

          {resumeMode === 'paste' ? (
            <div>
              <textarea
                className="textarea-input"
                rows={10}
                placeholder="Paste candidate resume text here (summary, skills, work history, projects, metrics)..."
                value={resumeText}
                onChange={(e) => setResumeText(e.target.value)}
              />
              <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 6, fontSize: '0.75rem', color: 'var(--text-dim)' }}>
                <span>Minimum 20 characters</span>
                <span>{resumeText.length} characters</span>
              </div>
            </div>
          ) : (
            <div>
              <label className="dropzone" style={{ display: 'block' }}>
                <input
                  type="file"
                  accept=".pdf,.docx,.txt"
                  style={{ display: 'none' }}
                  onChange={(e) => {
                    if (e.target.files?.[0]) setResumeFile(e.target.files[0]);
                  }}
                />
                <Upload size={32} color="#c084fc" style={{ margin: '0 auto 10px auto' }} />
                <p style={{ fontWeight: 600, fontSize: '0.9rem', marginBottom: 4 }}>
                  {resumeFile ? resumeFile.name : 'Click to upload or drag & drop'}
                </p>
                <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                  Supports PDF, DOCX, or TXT (Max 10MB)
                </p>
              </label>
              {resumeFile && (
                <div style={{ marginTop: 10, display: 'flex', alignItems: 'center', gap: 8, fontSize: '0.85rem', color: '#34d399' }}>
                  <CheckCircle2 size={16} />
                  <span>Selected: {resumeFile.name} ({(resumeFile.size / 1024).toFixed(1)} KB)</span>
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Action CTA */}
      <div style={{ textAlign: 'center', marginBottom: 45 }}>
        <button
          className="btn btn-primary"
          style={{ padding: '14px 36px', fontSize: '1.05rem', minWidth: 280 }}
          disabled={isLoading}
          onClick={handleProcessIntake}
        >
          {isLoading ? (
            <span>{loadingStep || 'Analyzing documents...'}</span>
          ) : (
            <>
              <span>Analyze Match & Prepare Interview</span>
              <ArrowRight size={18} />
            </>
          )}
        </button>
      </div>

      {/* Recent Sessions History */}
      {recentSessions && recentSessions.length > 0 && (
        <section className="glass-panel" style={{ padding: 24 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 16 }}>
            <Clock size={18} color="#94a3b8" />
            <h3 style={{ fontSize: '1rem', fontWeight: 600, color: '#e2e8f0' }}>Saved Practice Sessions</h3>
          </div>
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.875rem' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid var(--border-subtle)', textAlign: 'left', color: 'var(--text-dim)' }}>
                  <th style={{ padding: '10px 12px' }}>Role Title</th>
                  <th style={{ padding: '10px 12px' }}>Candidate</th>
                  <th style={{ padding: '10px 12px' }}>Level</th>
                  <th style={{ padding: '10px 12px' }}>Status</th>
                  <th style={{ padding: '10px 12px' }}>Score</th>
                  <th style={{ padding: '10px 12px', textAlign: 'right' }}>Action</th>
                </tr>
              </thead>
              <tbody>
                {recentSessions.map((s) => (
                  <tr key={s.id} style={{ borderBottom: '1px solid rgba(255, 255, 255, 0.04)' }}>
                    <td style={{ padding: '12px', fontWeight: 600 }}>{s.role_title || 'Software Role'}</td>
                    <td style={{ padding: '12px', color: 'var(--text-muted)' }}>{s.candidate_name || 'Candidate'}</td>
                    <td style={{ padding: '12px' }}>
                      <span className="badge badge-primary">{s.interview_level}</span>
                    </td>
                    <td style={{ padding: '12px' }}>
                      <span className={`badge ${s.status === 'completed' ? 'badge-success' : 'badge-warning'}`}>
                        {s.status}
                      </span>
                    </td>
                    <td style={{ padding: '12px', fontWeight: 700 }}>
                      {s.final_score !== null && s.final_score !== undefined ? `${s.final_score}/100` : 'In Progress'}
                    </td>
                    <td style={{ padding: '12px', textAlign: 'right' }}>
                      <button
                        className="btn btn-secondary"
                        style={{ padding: '4px 12px', fontSize: '0.8rem' }}
                        onClick={() => onResumeSession(s.id)}
                      >
                        {s.status === 'completed' ? 'View Report' : 'Resume'}
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      )}
    </div>
  );
};
