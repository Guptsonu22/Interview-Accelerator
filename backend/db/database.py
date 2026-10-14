import os
import sqlite3
import json
from contextlib import contextmanager
from typing import Generator, Any, Dict, List, Optional
from backend.core.config import settings

DB_FILE = settings.DATABASE_URL.replace("sqlite:///", "")


def get_db_path() -> str:
    """Return normalized local SQLite database path."""
    return os.path.abspath(DB_FILE)


def init_db() -> None:
    """Initialize SQLite database schema and tables."""
    db_path = get_db_path()
    os.makedirs(os.path.dirname(db_path) if os.path.dirname(db_path) else ".", exist_ok=True)

    with sqlite3.connect(db_path) as conn:
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA foreign_keys=ON;")
        cursor = conn.cursor()

        # Documents table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id TEXT PRIMARY KEY,
            doc_type TEXT NOT NULL, -- 'job_description' or 'resume'
            filename TEXT NOT NULL,
            raw_text TEXT NOT NULL,
            char_count INTEGER NOT NULL,
            parsed_metadata TEXT NOT NULL DEFAULT '{}',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # Job Analyses table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS job_analyses (
            id TEXT PRIMARY KEY,
            document_id TEXT NOT NULL,
            role_title TEXT NOT NULL,
            company_name TEXT NOT NULL DEFAULT 'Not specified',
            summary TEXT NOT NULL,
            responsibilities TEXT NOT NULL DEFAULT '[]',
            required_skills TEXT NOT NULL DEFAULT '[]',
            preferred_skills TEXT NOT NULL DEFAULT '[]',
            technical_competencies TEXT NOT NULL DEFAULT '[]',
            behavioral_competencies TEXT NOT NULL DEFAULT '[]',
            experience_level TEXT NOT NULL DEFAULT 'Not specified',
            education_requirements TEXT NOT NULL DEFAULT 'Not specified',
            tools_and_frameworks TEXT NOT NULL DEFAULT '[]',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(document_id) REFERENCES documents(id) ON DELETE CASCADE
        );
        """)

        # Candidate Analyses table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS candidate_analyses (
            id TEXT PRIMARY KEY,
            document_id TEXT NOT NULL,
            candidate_name TEXT NOT NULL DEFAULT 'Candidate',
            summary TEXT NOT NULL,
            technical_skills TEXT NOT NULL DEFAULT '[]',
            soft_skills TEXT NOT NULL DEFAULT '[]',
            education TEXT NOT NULL DEFAULT '[]',
            experience TEXT NOT NULL DEFAULT '[]',
            projects TEXT NOT NULL DEFAULT '[]',
            achievements TEXT NOT NULL DEFAULT '[]',
            quantified_claims TEXT NOT NULL DEFAULT '[]',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(document_id) REFERENCES documents(id) ON DELETE CASCADE
        );
        """)

        # Job Fit Assessments table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS job_fit_assessments (
            id TEXT PRIMARY KEY,
            job_analysis_id TEXT NOT NULL,
            candidate_analysis_id TEXT NOT NULL,
            overall_score INTEGER NOT NULL,
            required_skills_score INTEGER NOT NULL,
            preferred_skills_score INTEGER NOT NULL,
            project_evidence_score INTEGER NOT NULL,
            experience_score INTEGER NOT NULL,
            responsibility_score INTEGER NOT NULL,
            category_breakdown TEXT NOT NULL DEFAULT '{}',
            matched_skills TEXT NOT NULL DEFAULT '[]',
            partial_skills TEXT NOT NULL DEFAULT '[]',
            missing_skills TEXT NOT NULL DEFAULT '[]',
            key_reasons TEXT NOT NULL DEFAULT '[]',
            preparation_topics TEXT NOT NULL DEFAULT '[]',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(job_analysis_id) REFERENCES job_analyses(id) ON DELETE CASCADE,
            FOREIGN KEY(candidate_analysis_id) REFERENCES candidate_analyses(id) ON DELETE CASCADE
        );
        """)

        # Interview Sessions table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS interview_sessions (
            id TEXT PRIMARY KEY,
            job_analysis_id TEXT NOT NULL,
            candidate_analysis_id TEXT NOT NULL,
            job_fit_id TEXT NOT NULL,
            interview_level TEXT NOT NULL, -- 'screening', 'competency', 'deep_dive'
            status TEXT NOT NULL DEFAULT 'active', -- 'active', 'completed', 'cancelled'
            current_difficulty TEXT NOT NULL DEFAULT 'standard', -- 'fundamental', 'standard', 'challenging'
            current_question_index INTEGER NOT NULL DEFAULT 0,
            max_questions INTEGER NOT NULL DEFAULT 6,
            topics_covered TEXT NOT NULL DEFAULT '[]',
            weaknesses_identified TEXT NOT NULL DEFAULT '[]',
            strengths_identified TEXT NOT NULL DEFAULT '[]',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(job_analysis_id) REFERENCES job_analyses(id) ON DELETE CASCADE,
            FOREIGN KEY(candidate_analysis_id) REFERENCES candidate_analyses(id) ON DELETE CASCADE,
            FOREIGN KEY(job_fit_id) REFERENCES job_fit_assessments(id) ON DELETE CASCADE
        );
        """)

        # Interview Turns table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS interview_turns (
            id TEXT PRIMARY KEY,
            session_id TEXT NOT NULL,
            turn_index INTEGER NOT NULL,
            question_text TEXT NOT NULL,
            question_category TEXT NOT NULL,
            target_competency TEXT NOT NULL,
            candidate_answer TEXT NOT NULL DEFAULT '',
            candidate_transcript TEXT NOT NULL DEFAULT '',
            audio_used INTEGER NOT NULL DEFAULT 0,
            evaluation TEXT NOT NULL DEFAULT '{}',
            score INTEGER NOT NULL DEFAULT 0,
            feedback_good TEXT NOT NULL DEFAULT '',
            feedback_improve TEXT NOT NULL DEFAULT '',
            missing_concepts TEXT NOT NULL DEFAULT '[]',
            ideal_answer_direction TEXT NOT NULL DEFAULT '',
            follow_up_recommendation TEXT NOT NULL DEFAULT '',
            next_action TEXT NOT NULL DEFAULT 'continue',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(session_id) REFERENCES interview_sessions(id) ON DELETE CASCADE
        );
        """)

        # Performance Reports table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS performance_reports (
            id TEXT PRIMARY KEY,
            session_id TEXT UNIQUE NOT NULL,
            overall_score INTEGER NOT NULL,
            role_fit_score INTEGER NOT NULL,
            technical_knowledge_score INTEGER NOT NULL,
            problem_solving_score INTEGER NOT NULL,
            communication_score INTEGER NOT NULL,
            confidence_score INTEGER NOT NULL,
            depth_score INTEGER NOT NULL,
            behavioral_fit_score INTEGER NOT NULL,
            readiness_category TEXT NOT NULL, -- 'NOT READY', 'NEEDS PREPARATION', 'INTERVIEW READY', 'STRONG CANDIDATE'
            readiness_rationale TEXT NOT NULL,
            question_feedback_list TEXT NOT NULL DEFAULT '[]',
            demonstrated_strengths TEXT NOT NULL DEFAULT '[]',
            evidenced_weaknesses TEXT NOT NULL DEFAULT '[]',
            prioritized_prep_plan TEXT NOT NULL DEFAULT '[]',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(session_id) REFERENCES interview_sessions(id) ON DELETE CASCADE
        );
        """)

        conn.commit()


@contextmanager
def get_db_connection() -> Generator[sqlite3.Connection, None, None]:
    """Context manager for obtaining a database connection with dict-like row access."""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON;")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
