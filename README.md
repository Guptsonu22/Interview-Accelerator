# 🎯 Interview Accelerator
> **AI-Powered Role-Specific Interview Preparation & Candidate Readiness Engine**  
> *Built for EDXSO Assignment 3: AI Product Engineer Intern*

[![Test Suite](https://img.shields.io/badge/Pytest-14%2F14%20Passing-brightgreen?style=flat-square)](file:///c:/Users/Sonu/OneDrive/Desktop/Interview%20Accelerator/backend/tests)
[![Vite Build](https://img.shields.io/badge/Frontend-Vite%208%20%7C%20React%2019-blue?style=flat-square)](file:///c:/Users/Sonu/OneDrive/Desktop/Interview%20Accelerator/frontend)
[![Zero-Cost Demo Mode](https://img.shields.io/badge/Offline%20AI-Demo%20Provider%20Ready-success?style=flat-square)](file:///c:/Users/Sonu/OneDrive/Desktop/Interview%20Accelerator/.env.example)
[![Web Speech API](https://img.shields.io/badge/Voice%20Interaction-STT%20%2B%20TTS-orange?style=flat-square)](file:///c:/Users/Sonu/OneDrive/Desktop/Interview%20Accelerator/frontend/src/hooks)
[![Deployment](https://img.shields.io/badge/Docker-Multi--Stage%20Ready-purple?style=flat-square)](file:///c:/Users/Sonu/OneDrive/Desktop/Interview%20Accelerator/Dockerfile)

---

## 🌟 Executive Summary & Product Vision

### 🔍 Background & Pain Point Research
An in-depth analysis of candidate performance patterns and credibility benchmarks (referencing research from [StudentCredibility](https://studentcredibility.com/)) reveals a critical insight: **most students and early-career candidates fail interviews not because they lack raw technical ability, but because their competence is *under-evidenced* rather than under-qualified**.

Common interview pitfalls include:
1. **Generic Task Recitation vs. Quantified Outcomes**: Candidates list job duties ("responsible for building backend APIs") rather than architectural decisions and business impact ("engineered async pipeline reducing P99 latency by 42%").
2. **Missing STAR Structure**: Answers meander without structured *Situation, Task, Action, and Result*.
3. **Vague Claims Under Probing**: When asked deep-dive follow-up questions about concurrency, failure modes, or trade-offs, candidates fold because they rehearsed scripted answers rather than first-principles reasoning.
4. **Misaligned Preparation**: Job seekers spend weeks grinding generic LeetCode problems when the target role actually tests system architecture, API design, and cross-functional communication.

### 💡 The Solution: Interview Accelerator
**Interview Accelerator** bridges the gap between what an employer expects and what a candidate demonstrates. By parsing both the target Job Description (JD) and Candidate Resume, the platform:
- Evaluates role alignment using an **explainable 5-dimension Job Fit model**.
- Conducts an **adaptive, 3-level conversational interview** (Screening, Competency, Deep-Dive) that dynamically probes weaknesses and past claims.
- Features **real-time voice interaction** (browser Speech-to-Text with editable transcription buffer + Text-to-Speech spoken interviewer questions).
- Produces a **comprehensive diagnostic Performance Report** with 7 core competency scores, rubric-backed question evaluations, an actionable study roadmap, and deterministic readiness verdicts (`NOT READY`, `NEEDS PREPARATION`, `INTERVIEW READY`, `STRONG CANDIDATE`).

---

## 🏗️ System Architecture

```mermaid
flowchart TB
    subgraph Client [Frontend — React 19 + TypeScript 6 + Vite 8]
        UI[Glassmorphic UI & Design System]
        STT[Web Speech Recognition Hook\nLive Interim Transcript + Edit Buffer]
        TTS[Web Speech Synthesis Hook\nSpoken Questions + Audio Controls]
        State[Central Session & Persistent Cache]
    end

    subgraph Server [Backend — FastAPI + Python 3.14 + Pydantic v2]
        API[REST API Gateway & CORS Middleware]
        Security[Security Guardrails: Injection Filter & MIME Check]
        Parser[Document Parser: PDF (pypdf), DOCX (python-docx), Text]
        JobFitEngine[Deterministic Job Fit Engine (5 Dimensions)]
        InterviewEngine[Adaptive 3-Level Conversational Engine]
        ReportEngine[7-Competency Performance & Rubric Generator]
        DB[(SQLite WAL Database)]
    end

    subgraph AI [Modular AI Provider Layer]
        ProviderInterface[BaseLLMProvider Interface]
        DemoAI[Deterministic DemoProvider\nOffline / Zero-Cost / High-Fidelity]
        Gemini[Google Gemini API]
        OpenAI[OpenAI / Groq API]
    end

    UI <-->|HTTP / JSON| API
    UI <--> STT
    UI <--> TTS
    API --> Security
    Security --> Parser
    API --> JobFitEngine
    API --> InterviewEngine
    API --> ReportEngine
    InterviewEngine <--> ProviderInterface
    JobFitEngine <--> ProviderInterface
    ReportEngine <--> ProviderInterface
    ProviderInterface --> DemoAI
    ProviderInterface --> Gemini
    ProviderInterface --> OpenAI
    API <--> DB
```

---

## ✨ Key Features & Screen Breakdown

### 1. Document Intake & Validation Screen (`/`)
- **Multi-Format Ingestion**: Upload `.pdf` (via `pypdf`), `.docx` (via `python-docx`), or paste raw plain text.
- **One-Click Sample Previews**: Instantly load realistic sample data:
  - *Target JD*: Senior Full-Stack AI Engineer at Apex Systems.
  - *Candidate Resume*: Alex Rivera (Full-Stack AI Engineer with FastAPI, React, PyTorch).
- **Security & Prompt Injection Defenses**: File size limits (10MB), extension whitelisting, null byte stripping, and prompt injection pattern detection (`ignore previous instructions`, `system prompt:`, `override rules`).

### 2. Grounded Role & Job Fit Dashboard
- **Explainable Job Fit Score (0–100)** computed via a deterministic 5-dimension model:
  - **Required Skills Match (35%)**: Direct alignment with essential role competencies.
  - **Preferred Skills Match (15%)**: Bonus competencies and ecosystem tools.
  - **Project Evidence Alignment (20%)**: Verifiable project claims matching JD technologies.
  - **Responsibilities Alignment (15%)**: Semantic overlap with core day-to-day duties.
  - **Experience & Education (15%)**: Relevant years of experience and academic foundation.
- **Categorized Evidence Breakdown**:
  - 🟢 **Matched Competencies**: Explicitly demonstrated in resume.
  - 🟡 **Partial / Emerging**: Indirect or related exposure.
  - 🔴 **Missing Evidence**: Unaddressed requirements to prioritize.
- **Interview Mode Selector**: Select between **Level 1 (Screening)**, **Level 2 (Competency)**, and **Level 3 (Deep-Dive)**.

### 3. Adaptive Voice-Enabled Interview Room
- **3 Dynamic Interview Modes**:
  - **Level 1: Screening**: Evaluates career motivation, communication clarity, role fit, and high-level background.
  - **Level 2: Competency**: Focuses on core technical architecture, framework trade-offs, and practical design decisions.
  - **Level 3: Deep-Dive**: Probes edge cases, system bottlenecks, failure handling, and challenges unsubstantiated claims.
- **Dynamic Follow-Up Logic**: The AI analyzes the candidate's previous response, detects superficial answers or missing details, and dynamically tailors subsequent questions to probe uncovered weaknesses.
- **Real-Time Voice Interaction (Web Speech API)**:
  - 🎙️ **Speech-to-Text**: Real-time microphone listening with interim speech display.
  - ✏️ **Editable Review Buffer**: Candidates can edit or polish transcribed speech before submitting to prevent recognition errors.
  - 🔊 **Text-to-Speech**: Spoken AI interviewer questions with voice pitch/rate tuning, replay, pause, and mute controls.
  - ⌨️ **Accessible Text Fallback**: Seamless typing mode for environments without microphone access.

### 4. Comprehensive Performance Report & Diagnostic Analytics
- **Overall Score (0–100)**: Weighted evaluation of all responses against role requirements.
- **7 Core Competency Diagnostics**:
  1. **Role Fit**: Alignment with job level and specific role requirements.
  2. **Technical Knowledge**: Depth and accuracy of core engineering principles.
  3. **Problem Solving**: Systematic thinking, trade-off reasoning, and edge case anticipation.
  4. **Communication**: Clarity, conciseness, and articulation of complex technical concepts.
  5. **Confidence**: Decisiveness, tone, and poise under challenging probing.
  6. **Depth of Understanding**: First-principles comprehension beyond superficial buzzwords.
  7. **Behavioral Fit**: Ownership, STAR structure, collaboration, and learning agility.
- **Question-by-Question Rubric Breakdown**:
  - Candidate's submitted answer.
  - Point score (0–100) and rubric criteria (Relevance, Technical Correctness, Depth, STAR Reasoning, Clarity).
  - Highlighted strengths (*What was good*) and weaknesses (*Areas for improvement*).
  - **Ideal Answer Guide**: Exemplary model answer demonstrating best practices.
  - **Targeted Practice Recommendation**: Actionable drill for rapid improvement.
- **Prioritized Preparation Plan**: Step-by-step revision roadmap with specific concepts, practical exercises, and measurable completion criteria.
- **Deterministic Interview Readiness Rating**:
  - `STRONG CANDIDATE`: Score ≥ 85 and all competencies ≥ 70.
  - `INTERVIEW READY`: Score ≥ 70 and all competencies ≥ 55.
  - `NEEDS PREPARATION`: Score ≥ 50.
  - `NOT READY`: Score < 50.
- **Export Capabilities**: Clean Markdown download (`.md`) and browser print-to-PDF formatting.

---

## 🧮 Mathematical & Scoring Formulas

### 1. Deterministic Job Fit Formula
$$\text{Job Fit Score} = (S_{\text{req}} \times 0.35) + (S_{\text{pref}} \times 0.15) + (S_{\text{proj}} \times 0.20) + (S_{\text{resp}} \times 0.15) + (S_{\text{exp}} \times 0.15)$$

Where:
- $S_{\text{req}} = \min\left(100, \frac{|\text{Matched}_{\text{req}}| \times 1.0 + |\text{Partial}_{\text{req}}| \times 0.5}{|\text{Total}_{\text{req}}|} \times 100\right)$
- $S_{\text{pref}} = \min\left(100, \frac{|\text{Matched}_{\text{pref}}| \times 1.0 + |\text{Partial}_{\text{pref}}| \times 0.5}{|\text{Total}_{\text{pref}}|} \times 100\right)$
- $S_{\text{proj}} = \text{base}(40) + \min(40, |\text{Projects}| \times 15) + 20 \times \mathbb{I}(\text{tech match})$
- $S_{\text{resp}} = \min\left(100, \frac{\text{Matched Responsibilities}}{\text{Total Responsibilities}} \times 100 + 20\right)$
- $S_{\text{exp}} = 50 + \min(35, |\text{Experience Items}| \times 15) + 15 \times \mathbb{I}(\text{degree present})$

### 2. Multi-Factor Turn Evaluation Rubric
Each candidate response is scored across 5 rubric vectors (0–100 each):
$$\text{Turn Score} = (R \times 0.25) + (T \times 0.25) + (D \times 0.20) + (S \times 0.15) + (C \times 0.15)$$
- **$R$ (Relevance - 25%)**: Directly addresses the specific question asked.
- **$T$ (Technical Correctness - 25%)**: Free of factual mistakes and sound in implementation logic.
- **$D$ (Depth & Nuance - 20%)**: Discusses trade-offs, edge cases, and performance implications.
- **$S$ (STAR / Structured Reasoning - 15%)**: Follows Situation $\rightarrow$ Task $\rightarrow$ Action $\rightarrow$ Result.
- **$C$ (Clarity & Articulation - 15%)**: Crisp, professional, and well-structured communication.

---

## 🔌 AI Provider Architecture & Offline Demo Mode

The application uses an interchangeable provider abstraction (`backend/services/llm_provider.py`) so it runs seamlessly in any environment:

| Provider | Mode | API Key Required? | Description |
| :--- | :--- | :--- | :--- |
| **DemoProvider** (Default) | Offline | ❌ **None** | High-fidelity, deterministic AI simulation. Extracts grounded entities, generates contextual questions, evaluates rubrics, and calculates scores with zero latency and zero cost. Clearly badged in the UI. |
| **Google Gemini** | Cloud | `GEMINI_API_KEY` | Calls Gemini 1.5 Flash / Pro via official Google SDK with structured JSON schemas. |
| **OpenAI** | Cloud | `OPENAI_API_KEY` | Calls GPT-4o / GPT-4o-mini using OpenAI Python SDK. |
| **Groq** | Cloud | `GROQ_API_KEY` | Ultra-fast Llama-3-70b inference with OpenAI-compatible endpoint. |

Switching providers is done via a single environment variable in `.env`:
```env
LLM_PROVIDER=demo       # "demo", "gemini", "openai", or "groq"
```

---

## 🚀 Quick Start Guide (Windows PowerShell & Linux/macOS)

### Prerequisites
- **Python 3.10+** (Python 3.14 supported)
- **Node.js 18+** (Node 20+ recommended)
- **Git**

### 1. Clone the Repository
```powershell
git clone https://github.com/Guptsonu22/Interview-Accelerator.git
cd "Interview Accelerator"
```

### 2. Environment Configuration
Copy `.env.example` to `.env`:
```powershell
Copy-Item .env.example .env
```
*(By default, `LLM_PROVIDER=demo` is pre-configured, allowing the app to run immediately without any paid API keys).*

---

### 3. Running Locally (Dual Dev Server Mode)

#### Terminal 1 — Start the FastAPI Backend
```powershell
# Install backend dependencies
python -m pip install -r backend/requirements.txt

# Start backend server with uvicorn
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```
*Backend will be running at `http://127.0.0.1:8000` (Swagger docs at `http://127.0.0.1:8000/docs`).*

#### Terminal 2 — Start the Vite React Frontend
```powershell
cd frontend
npm install
npm run dev -- --host 127.0.0.1 --port 5173
```
*Frontend will be running at `http://127.0.0.1:5173`.*

---

### 4. Running Unified Production Mode (Single Port 8000)
The FastAPI backend is configured to automatically serve the compiled React SPA from `frontend/dist` on port 8000:
```powershell
# 1. Build frontend assets
cd frontend
npm run build
cd ..

# 2. Run backend (serves both API and SPA)
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```
*Visit `http://127.0.0.1:8000` in any modern web browser to access the entire application!*

---

## 🐳 Docker Deployment

A multi-stage `Dockerfile` is provided that builds the React application and packages it alongside FastAPI in a slim Python 3.11 environment.

### Build and Run with Docker
```bash
# Build Docker image
docker build -t interview-accelerator .

# Run container
docker run -p 8000:8000 -e LLM_PROVIDER=demo interview-accelerator
```

### Or using Docker Compose
```bash
docker-compose up --build
```
Access the application at `http://localhost:8000`.

---

## 🧪 Automated Testing & Verification

The project includes automated Pytest backend test suites covering all core logic:
```powershell
python -m pytest -v
```

### Test Coverage Highlights:
- ✅ `test_job_analysis_extraction`: Validates structured JD entity parsing.
- ✅ `test_candidate_analysis_extraction`: Validates resume experience, skills, and projects parsing.
- ✅ `test_job_fit_deterministic_calculation`: Validates 5-dimension weighting and score reproducibility.
- ✅ `test_health_endpoint`: Checks `/api/health` and SQLite DB connectivity.
- ✅ `test_document_paste_and_analysis_api`: Tests end-to-end HTTP intake and analysis pipeline.
- ✅ `test_sanitize_text`: Validates text normalization and character cleaning.
- ✅ `test_validate_file_upload_valid`: Checks valid PDF and DOCX uploads.
- ✅ `test_validate_file_upload_invalid_ext`: Rejects unauthorized file extensions (.exe, .sh).
- ✅ `test_validate_file_upload_empty`: Rejects 0-byte uploaded documents.
- ✅ `test_prompt_injection_detection`: Detects malicious instructions and sanitizes inputs.
- ✅ `test_parse_text_bytes`: Validates UTF-8 raw text extraction.
- ✅ `test_parse_docx_bytes`: Tests Word document binary stream extraction.
- ✅ `test_parse_file_too_short`: Rejects insufficient input content.
- ✅ `test_interview_full_flow`: Validates full 3-turn interview session, dynamic question transitions, answer evaluation, 7-competency aggregation, and performance report generation.

**Pytest Status**: `14 passed in 2.34s`.  
**Frontend Build Status**: `tsc -b && vite build` completed cleanly with zero warnings (`dist/` generated).

---

## 🎬 Demo Video Walkthrough Script (3–5 Minutes)

When recording a screencast demonstration for submission, follow this structured walkthrough:

| Time | Scene | Talking Points & Actions |
| :--- | :--- | :--- |
| **0:00 – 0:45** | **Introduction & Problem Statement** | • Introduce the problem: candidates are under-evidenced rather than under-qualified (StudentCredibility reference).<br>• Show the high-craft glassmorphic landing page.<br>• Click `Load Sample JD` and `Load Sample Resume` to demonstrate rapid intake.<br>• Click `Analyze Role Match & Job Fit`. |
| **0:45 – 1:30** | **Job Fit & Evidence Analysis** | • Walk through the **Explainable 78/100 Job Fit Score**.<br>• Highlight the 5 weighted dimensions (Required Skills 35%, Projects 20%, etc.).<br>• Point out the categorized skill breakdown: Matched, Partial, Missing.<br>• Highlight the offline `Demo Mode (Offline AI)` badge showing zero paid API dependency.<br>• Select **Level 2: Competency** or **Level 3: Deep-Dive** and click `Begin Interview Session`. |
| **1:30 – 3:00** | **Adaptive Voice Interview Room** | • Show the AI interviewer asking question 1.<br>• Click `🔊 Replay Question` to demonstrate Web Speech TTS playback.<br>• Click `🎙️ Speak Answer` to demonstrate browser SpeechRecognition.<br>• Speak into the microphone, showing the real-time interim transcript appearing in the editor.<br>• Demonstrate editing the transcript in the review textarea.<br>• Submit the answer and observe the AI formulating dynamic follow-up Question 2 based on the candidate's answer.<br>• Complete remaining questions to trigger final report generation. |
| **3:00 – 4:30** | **Diagnostic Performance Report** | • Walk through the **Overall Score (82/100)** and **Interview Ready** verdict.<br>• Review the **7 Core Competency Diagnostics** (Role Fit, Technical Knowledge, Problem Solving, Communication, Confidence, Depth, Behavioral Fit).<br>• Open a question evaluation: show candidate answer, rubric score, strengths, areas for improvement, and the **Ideal Model Answer**.<br>• Review the **Prioritized Preparation Plan** with practical study drills.<br>• Click `Download Markdown Report` and `Print / Save as PDF` to prove export functionality. |
| **4:30 – 5:00** | **Engineering & Architecture Summary** | • Highlight FastAPI + Pydantic v2 + SQLite WAL backend.<br>• Mention 14/14 Pytest tests passing.<br>• Conclude on how Interview Accelerator creates confident, job-ready candidates. |

---

## 📂 Project Structure

```text
Interview Accelerator/
├── backend/
│   ├── api/
│   │   └── routes/
│   │       ├── health.py           # Health check & system diagnostic endpoint
│   │       ├── documents.py        # File upload & text ingestion endpoint
│   │       ├── analysis.py         # Grounded JD/resume analysis & Job Fit
│   │       ├── interview.py        # Conversational interview session manager
│   │       └── reports.py          # 7-competency report generator & export
│   ├── core/
│   │   ├── config.py               # Pydantic v2 Settings & environment parsing
│   │   └── security.py             # MIME validation & prompt injection defenses
│   ├── db/
│   │   ├── database.py             # SQLite WAL connection & table creation
│   │   └── models.py               # Document, Analysis, Session, Turn DAOs
│   ├── schemas/
│   │   ├── documents.py            # Pydantic document models
│   │   ├── analysis.py             # Structured JD & resume schemas
│   │   ├── interview.py            # Turn & question transition schemas
│   │   └── reports.py              # Performance report & competency schemas
│   ├── services/
│   │   ├── document_parser.py      # PDF (pypdf), DOCX, and text parsers
│   │   ├── job_fit.py              # Deterministic 5-dimension Job Fit engine
│   │   ├── llm_provider.py         # Modular AI provider (Demo, Gemini, OpenAI)
│   │   ├── interview_engine.py     # 3-level adaptive interview state machine
│   │   └── report_generator.py     # Rubric aggregator & study plan generator
│   ├── tests/
│   │   ├── test_analysis.py        # JD/resume extraction & job fit tests
│   │   ├── test_api.py             # FastAPI route integration tests
│   │   ├── test_documents.py       # File parser & security validation tests
│   │   └── test_interview.py       # Full interview loop & report tests
│   ├── main.py                     # FastAPI application & SPA static server
│   └── requirements.txt            # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Navbar.tsx          # Branding, provider badge, reset button
│   │   │   ├── IntakeScreen.tsx    # Upload, paste, sample data prefill
│   │   │   ├── AnalysisScreen.tsx  # Job fit score, skills breakdown, round select
│   │   │   ├── InterviewRoomScreen.tsx # Voice controls, STT editor, waveform
│   │   │   └── ReportScreen.tsx    # 7 competencies, rubrics, roadmap, export
│   │   ├── hooks/
│   │   │   ├── useSpeechRecognition.ts # Web Speech API transcription hook
│   │   │   └── useSpeechSynthesis.ts   # Web Speech API question reader hook
│   │   ├── services/
│   │   │   └── api.ts              # Typed Axios HTTP client
│   │   ├── App.tsx                 # View state machine & session restore
│   │   ├── main.tsx                # React DOM entry point
│   │   └── index.css               # Bespoke glassmorphism design system
│   ├── index.html                  # HTML5 container with Space Grotesk fonts
│   ├── package.json                # React 19, TypeScript 6, Vite 8, Lucide
│   ├── tsconfig.json               # TypeScript strict configuration
│   └── vite.config.ts              # Vite proxy configuration
├── Dockerfile                      # Multi-stage production container
├── docker-compose.yml              # Local container orchestration
├── IMPLEMENTATION_PLAN.md          # Phased roadmap & verification checklist
├── .env.example                    # Template environment variables
├── .gitignore                      # Git exclusion rules
├── powershell.cmd                  # Windows PowerShell command shim
└── python.cmd                      # Windows Python 3.14 command shim
```

---

## 🔒 Security & Data Privacy
- **Client-Side Voice Processing**: Voice transcription and synthesis are executed natively via the client browser's Web Speech API. Audio data is not streamed to or stored on third-party speech servers.
- **Prompt Injection Neutralization**: All user inputs undergo sanitization to prevent prompt hijacking or instruction override attacks.
- **Local Persistence**: User sessions and reports are stored locally in an embedded SQLite database using Write-Ahead Logging (`WAL` mode). No user data is sent to external databases.
- **No Paid API Dependency**: Out of the box, `DemoProvider` simulates all AI functionality deterministically with zero remote data transfer.

---

## 📄 License & Attribution
Developed for **EDXSO Assignment 3: AI Product Engineer Intern — Interview Accelerator**.  
Built with FastAPI, React 19, Vite, and modern Web Standards.
