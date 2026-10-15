import React, { useState, useEffect } from 'react';
import type {
  InterviewSession,
  InterviewTurn,
  PerformanceReport
} from '../types';
import { api } from '../services/api';
import { useSpeechRecognition } from '../hooks/useSpeechRecognition';
import { useSpeechSynthesis } from '../hooks/useSpeechSynthesis';
import {
  Mic,
  MicOff,
  Volume2,
  VolumeX,
  Play,
  Pause,
  RotateCcw,
  Send,
  Sparkles,
  CheckCircle2,
  ChevronDown,
  ChevronUp,
  Camera,
  CameraOff
} from 'lucide-react';

interface InterviewRoomScreenProps {
  session: InterviewSession;
  initialTurn: InterviewTurn;
  roleTitle: string;
  candidateName: string;
  onFinishSession: (report: PerformanceReport) => void;
}

export const InterviewRoomScreen: React.FC<InterviewRoomScreenProps> = ({
  session,
  initialTurn,
  onFinishSession,
}) => {
  const [currentSession, setCurrentSession] = useState<InterviewSession>(session);
  const [currentTurn, setCurrentTurn] = useState<InterviewTurn>(initialTurn);
  const [allTurns, setAllTurns] = useState<InterviewTurn[]>([initialTurn]);
  const [answerText, setAnswerText] = useState<string>('');
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [lastEvaluation, setLastEvaluation] = useState<InterviewTurn | null>(null);
  const [showHistory, setShowHistory] = useState<boolean>(false);

  // Video State & Refs
  const [isVideoEnabled, setIsVideoEnabled] = useState<boolean>(false);
  const [videoNotice, setVideoNotice] = useState<string | null>(null);
  const videoRef = React.useRef<HTMLVideoElement | null>(null);
  const mediaStreamRef = React.useRef<MediaStream | null>(null);

  // Voice Hooks
  const speechRecognition = useSpeechRecognition();
  const speechSynthesis = useSpeechSynthesis();

  // Speak question automatically when a new question arrives (if not muted)
  useEffect(() => {
    if (currentTurn?.question_text && !speechSynthesis.isMuted) {
      speechSynthesis.speak(currentTurn.question_text);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [currentTurn?.id]);

  // Sync speech recognition transcript into candidate answer text
  useEffect(() => {
    if (speechRecognition.transcript) {
      setAnswerText((prev) => (prev !== speechRecognition.transcript ? speechRecognition.transcript : prev));
    }
  }, [speechRecognition.transcript]);

  // Video Stream Lifecycle
  const handleToggleVideo = async () => {
    if (isVideoEnabled) {
      if (mediaStreamRef.current) {
        mediaStreamRef.current.getTracks().forEach((track) => track.stop());
        mediaStreamRef.current = null;
      }
      setIsVideoEnabled(false);
      setVideoNotice(null);
    } else {
      setVideoNotice(null);
      try {
        if (!navigator?.mediaDevices?.getUserMedia) {
          setVideoNotice('Webcam access is not supported by your browser environment. Voice and text modes remain active.');
          return;
        }
        const stream = await navigator.mediaDevices.getUserMedia({
          video: { width: 480, height: 360 },
          audio: false,
        });
        mediaStreamRef.current = stream;
        setIsVideoEnabled(true);
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
        }
      } catch {
        setVideoNotice('Camera permission was not granted or no webcam was detected. You can seamlessly proceed using voice or text.');
        setIsVideoEnabled(false);
      }
    }
  };

  useEffect(() => {
    if (isVideoEnabled && videoRef.current && mediaStreamRef.current) {
      videoRef.current.srcObject = mediaStreamRef.current;
    }
  }, [isVideoEnabled]);

  useEffect(() => {
    return () => {
      if (mediaStreamRef.current) {
        mediaStreamRef.current.getTracks().forEach((track) => track.stop());
      }
    };
  }, []);

  const handleToggleMic = () => {
    if (speechRecognition.isListening) {
      speechRecognition.stopListening();
    } else {
      speechRecognition.startListening();
    }
  };

  const handleSubmitAnswer = async () => {
    if (answerText.trim().length < 5) {
      setErrorMsg('Please formulate an answer with at least 5 characters before submitting.');
      return;
    }

    if (speechRecognition.isListening) {
      speechRecognition.stopListening();
    }
    speechSynthesis.cancel();

    setIsSubmitting(true);
    setErrorMsg(null);

    try {
      const audioUsed = speechRecognition.transcript.trim().length > 0;
      const result = await api.submitAnswer(
        currentSession.id,
        answerText.trim(),
        speechRecognition.transcript,
        audioUsed
      );

      setCurrentSession(result.session);
      setLastEvaluation(result.evaluated_turn);
      setAllTurns(result.all_turns);

      // Reset input for next question
      setAnswerText('');
      speechRecognition.resetTranscript();

      if (result.is_completed || !result.next_turn) {
        // Generate final report
        const report = await api.getReport(currentSession.id);
        onFinishSession(report);
      } else {
        setCurrentTurn(result.next_turn);
      }
    } catch (err: any) {
      setErrorMsg(err.message || 'Failed to submit answer.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleFinishEarly = async () => {
    if (window.confirm('Are you sure you want to finish the interview early and generate the performance report?')) {
      speechSynthesis.cancel();
      if (speechRecognition.isListening) speechRecognition.stopListening();
      try {
        await api.finishInterviewEarly(currentSession.id);
        const report = await api.getReport(currentSession.id);
        onFinishSession(report);
      } catch (err: any) {
        setErrorMsg(err.message || 'Could not finalize report.');
      }
    }
  };

  const progressPercent = Math.round(
    ((currentSession.current_question_index + 1) / currentSession.max_questions) * 100
  );

  return (
    <div className="animate-fade-in">
      {/* Session Header Status */}
      <div
        className="glass-panel"
        style={{
          padding: '16px 24px',
          marginBottom: 20,
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: 12,
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <span className="badge badge-primary" style={{ textTransform: 'uppercase' }}>
            {currentSession.interview_level.replace('_', ' ')}
          </span>
          <span
            className={`badge ${
              currentSession.current_difficulty === 'challenging'
                ? 'badge-danger'
                : currentSession.current_difficulty === 'fundamental'
                ? 'badge-warning'
                : 'badge-success'
            }`}
          >
            Difficulty: {currentSession.current_difficulty}
          </span>
          <span style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>
            Question {currentSession.current_question_index + 1} of {currentSession.max_questions}
          </span>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
          <div style={{ width: 140, height: 6, background: 'rgba(255, 255, 255, 0.1)', borderRadius: 3, overflow: 'hidden' }}>
            <div style={{ width: `${progressPercent}%`, height: '100%', background: '#6366f1', borderRadius: 3 }} />
          </div>

          <button
            className="btn btn-secondary"
            style={{ fontSize: '0.8rem', padding: '6px 12px' }}
            onClick={handleFinishEarly}
          >
            Finish Early & View Report
          </button>
        </div>
      </div>

      {errorMsg && (
        <div style={{ background: 'rgba(239, 68, 68, 0.12)', border: '1px solid rgba(239, 68, 68, 0.3)', borderRadius: 12, padding: 14, marginBottom: 16, color: '#fca5a5' }}>
          {errorMsg}
        </div>
      )}

      {/* AI Interviewer Card */}
      <section className="glass-panel" style={{ padding: 28, marginBottom: 20 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <div
              style={{
                width: 44,
                height: 44,
                borderRadius: '50%',
                background: 'linear-gradient(135deg, #6366f1, #8b5cf6)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                boxShadow: speechSynthesis.isSpeaking ? '0 0 20px #818cf8' : 'none',
                transition: 'all 0.3s ease',
              }}
            >
              <Sparkles size={22} color="#fff" />
            </div>
            <div>
              <h2 style={{ fontSize: '1.05rem', fontWeight: 600 }}>AI Hiring Interviewer</h2>
              <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                {speechSynthesis.isSpeaking ? 'Speaking question aloud...' : 'Listening / Waiting for response'}
              </p>
            </div>
          </div>

          {/* Voice Controls */}
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <button
              id="btn-voice-play-pause"
              className="btn btn-secondary"
              style={{ padding: '6px 12px', fontSize: '0.8rem' }}
              onClick={() => {
                if (speechSynthesis.isSpeaking) {
                  speechSynthesis.pause();
                } else if (speechSynthesis.isPaused) {
                  speechSynthesis.resume();
                } else {
                  speechSynthesis.speak(currentTurn.question_text);
                }
              }}
              title="Play or Pause question audio"
            >
              {speechSynthesis.isSpeaking ? <Pause size={14} /> : <Play size={14} />}
              <span>{speechSynthesis.isSpeaking ? 'Pause' : 'Re-speak'}</span>
            </button>

            <button
              id="btn-voice-mute"
              className="btn btn-secondary"
              style={{ padding: '6px 10px' }}
              onClick={speechSynthesis.toggleMute}
              title={speechSynthesis.isMuted ? 'Unmute voice' : 'Mute voice'}
            >
              {speechSynthesis.isMuted ? <VolumeX size={16} color="#fca5a5" /> : <Volume2 size={16} />}
            </button>
          </div>
        </div>

        {/* Current Question Display */}
        <div style={{ padding: '20px 24px', background: 'rgba(10, 15, 26, 0.75)', borderRadius: 14, border: '1px solid var(--border-subtle)', marginBottom: 14 }}>
          <div style={{ display: 'flex', gap: 8, marginBottom: 8 }}>
            <span className="badge badge-primary">{currentTurn.question_category}</span>
            <span className="badge badge-warning">Target: {currentTurn.target_competency}</span>
          </div>
          <p id="current-question-text" style={{ fontSize: '1.25rem', fontWeight: 600, lineHeight: 1.5, color: '#ffffff' }}>
            "{currentTurn.question_text}"
          </p>
        </div>
      </section>

      {/* Candidate Voice & Input Area */}
      <section className="glass-panel" style={{ padding: 28, marginBottom: 20 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 14 }}>
          <h3 style={{ fontSize: '1rem', fontWeight: 600, color: '#e2e8f0' }}>Your Candidate Response</h3>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            {speechRecognition.isListening && (
              <div className="waveform-container">
                <div className="waveform-bar" />
                <div className="waveform-bar" />
                <div className="waveform-bar" />
                <div className="waveform-bar" />
                <div className="waveform-bar" />
              </div>
            )}
            <span
              className={`badge ${speechRecognition.isListening ? 'badge-danger' : 'badge-secondary'}`}
              style={{ fontSize: '0.8rem' }}
            >
              {speechRecognition.isListening ? '● Recording Speech' : 'Mic Idle'}
            </span>
          </div>
        </div>

        {/* Browser Voice Recognition Support Notice */}
        {!speechRecognition.isSupported && (
          <div style={{ padding: '10px 14px', background: 'rgba(245, 158, 11, 0.1)', border: '1px solid rgba(245, 158, 11, 0.25)', borderRadius: 10, fontSize: '0.8rem', color: '#fbbf24', marginBottom: 14 }}>
            Browser notice: Web Speech Recognition is supported in Chrome, Edge, and Chromium browsers. On other browsers, you can seamlessly type your answer below.
          </div>
        )}

        {/* Big Mic Button & Controls Bar */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 14, marginBottom: 16 }}>
          <button
            id="btn-mic-record"
            className={`btn ${speechRecognition.isListening ? 'btn-danger' : 'btn-primary'}`}
            style={{
              padding: '12px 24px',
              fontSize: '0.95rem',
              borderRadius: 30,
              boxShadow: speechRecognition.isListening ? '0 0 25px rgba(239, 68, 68, 0.5)' : undefined,
            }}
            onClick={handleToggleMic}
            disabled={!speechRecognition.isSupported}
          >
            {speechRecognition.isListening ? <MicOff size={18} /> : <Mic size={18} />}
            <span>{speechRecognition.isListening ? 'Stop Recording' : 'Speak Answer (Microphone)'}</span>
          </button>

          <button
            id="btn-toggle-video"
            type="button"
            className={`btn ${isVideoEnabled ? 'btn-primary' : 'btn-secondary'}`}
            style={{
              padding: '12px 20px',
              fontSize: '0.95rem',
              borderRadius: 30,
            }}
            onClick={handleToggleVideo}
            title={isVideoEnabled ? 'Turn off camera' : 'Enable live camera preview (Video Interview Mode)'}
          >
            {isVideoEnabled ? <CameraOff size={18} /> : <Camera size={18} />}
            <span>{isVideoEnabled ? 'Disable Camera' : 'Video Mode (Camera)'}</span>
          </button>

          {answerText && (
            <button
              id="btn-clear-answer"
              className="btn btn-secondary"
              style={{ padding: '10px 16px', fontSize: '0.85rem' }}
              onClick={() => {
                setAnswerText('');
                speechRecognition.resetTranscript();
              }}
            >
              <RotateCcw size={14} />
              <span>Clear Text</span>
            </button>
          )}
        </div>

        {/* Video Mode Notice if permission denied */}
        {videoNotice && (
          <div style={{ padding: '10px 14px', background: 'rgba(239, 68, 68, 0.1)', border: '1px solid rgba(239, 68, 68, 0.25)', borderRadius: 10, fontSize: '0.8rem', color: '#fca5a5', marginBottom: 14 }}>
            {videoNotice}
          </div>
        )}

        {/* Live Video Camera Tile (when enabled) */}
        {isVideoEnabled && (
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: 16,
              padding: 14,
              marginBottom: 16,
              background: 'rgba(15, 23, 42, 0.75)',
              border: '1px solid rgba(99, 102, 241, 0.3)',
              borderRadius: 14,
            }}
          >
            <div
              style={{
                position: 'relative',
                width: 180,
                height: 135,
                borderRadius: 10,
                overflow: 'hidden',
                background: '#090d16',
                border: '1px solid rgba(99, 102, 241, 0.4)',
                flexShrink: 0,
              }}
            >
              <video
                ref={videoRef}
                autoPlay
                playsInline
                muted
                style={{ width: '100%', height: '100%', objectFit: 'cover', transform: 'scaleX(-1)' }}
              />
              <div
                style={{
                  position: 'absolute',
                  bottom: 6,
                  left: 6,
                  background: 'rgba(0, 0, 0, 0.7)',
                  padding: '2px 6px',
                  borderRadius: 4,
                  fontSize: '0.65rem',
                  color: '#4ade80',
                  display: 'flex',
                  alignItems: 'center',
                  gap: 4,
                }}
              >
                <span style={{ width: 5, height: 5, borderRadius: '50%', background: '#4ade80' }} />
                Camera Live
              </div>
            </div>
            <div>
              <h4 style={{ fontSize: '0.9rem', fontWeight: 600, color: '#f1f5f9', marginBottom: 4 }}>
                Video Interview Mode Active
              </h4>
              <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)', lineHeight: 1.4 }}>
                Your webcam is active locally for posture review and authentic interview practice. No video data is recorded or transmitted externally.
              </p>
            </div>
          </div>
        )}

        {/* Transcript Review and Correction Textarea */}
        <div className="form-group" style={{ marginBottom: 16 }}>
          <label className="form-label">
            <span>Answer Text & Transcript Review (Editable before submission):</span>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }}>{answerText.length} characters</span>
          </label>
          <textarea
            id="textarea-candidate-answer"
            data-testid="candidate-answer"
            className="textarea-input"
            rows={6}
            placeholder="Your spoken words will appear here in real time. You can review, edit, or freely type your answer..."
            value={answerText}
            onChange={(e) => setAnswerText(e.target.value)}
          />
        </div>

        {/* Submit Action */}
        <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 12 }}>
          <button
            id="btn-submit-answer"
            data-testid="submit-answer"
            className="btn btn-primary"
            style={{ padding: '12px 32px', fontSize: '1rem', minWidth: 200 }}
            disabled={isSubmitting || answerText.trim().length < 5}
            onClick={handleSubmitAnswer}
          >
            {isSubmitting ? (
              <span>Evaluating Answer...</span>
            ) : (
              <>
                <Send size={16} />
                <span>Submit Answer</span>
              </>
            )}
          </button>
        </div>
      </section>

      {/* Immediate Real-time Turn Evaluation Card (if available from previous submission) */}
      {lastEvaluation && lastEvaluation.score > 0 && (
        <section className="glass-panel" style={{ padding: 24, marginBottom: 20, border: '1px solid rgba(99, 102, 241, 0.3)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
            <h3 style={{ fontSize: '1.05rem', fontWeight: 600, display: 'flex', alignItems: 'center', gap: 8 }}>
              <CheckCircle2 size={18} color="#34d399" />
              <span>Turn Feedback (Score: {lastEvaluation.score}/100)</span>
            </h3>
            <span className="badge badge-primary">Rubric Evaluated</span>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: 16, fontSize: '0.85rem' }}>
            <div style={{ background: 'rgba(16, 185, 129, 0.05)', padding: 12, borderRadius: 8, border: '1px solid rgba(16, 185, 129, 0.2)' }}>
              <strong style={{ color: '#34d399', display: 'block', marginBottom: 4 }}>What was good:</strong>
              <p style={{ color: '#e2e8f0' }}>{lastEvaluation.feedback_good}</p>
            </div>
            <div style={{ background: 'rgba(245, 158, 11, 0.05)', padding: 12, borderRadius: 8, border: '1px solid rgba(245, 158, 11, 0.2)' }}>
              <strong style={{ color: '#fbbf24', display: 'block', marginBottom: 4 }}>What could be improved:</strong>
              <p style={{ color: '#e2e8f0' }}>{lastEvaluation.feedback_improve}</p>
            </div>
          </div>
        </section>
      )}

      {/* Conversation History Drawer */}
      <section className="glass-panel" style={{ padding: 20 }}>
        <div
          onClick={() => setShowHistory(!showHistory)}
          style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', cursor: 'pointer' }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <h3 style={{ fontSize: '0.95rem', fontWeight: 600 }}>Previous Turns History ({allTurns.filter(t => t.candidate_answer).length})</h3>
          </div>
          {showHistory ? <ChevronUp size={18} /> : <ChevronDown size={18} />}
        </div>

        {showHistory && (
          <div style={{ marginTop: 16, display: 'flex', flexDirection: 'column', gap: 14 }}>
            {allTurns
              .filter((t) => t.candidate_answer)
              .map((t, idx) => (
                <div key={t.id || idx} style={{ padding: 14, background: 'rgba(10, 15, 26, 0.6)', borderRadius: 10, border: '1px solid var(--border-subtle)' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', color: 'var(--text-dim)', marginBottom: 6 }}>
                    <span>Question {t.turn_index + 1} · {t.question_category}</span>
                    <strong style={{ color: '#a5b4fc' }}>Score: {t.score}/100</strong>
                  </div>
                  <p style={{ fontWeight: 600, fontSize: '0.9rem', marginBottom: 6 }}>Q: {t.question_text}</p>
                  <p style={{ fontSize: '0.85rem', color: '#cbd5e1', fontStyle: 'italic', marginBottom: 8 }}>
                    A: "{t.candidate_answer}"
                  </p>
                  <div style={{ fontSize: '0.8rem', color: '#94a3b8' }}>
                    <span style={{ color: '#34d399' }}>✓ {t.feedback_good}</span>
                  </div>
                </div>
              ))}
          </div>
        )}
      </section>
    </div>
  );
};
