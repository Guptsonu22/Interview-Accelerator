# EDXSO Assignment 3: AI Product Engineer Intern
# FINAL SUBMISSION — INTERVIEW ACCELERATOR

**Candidate**: Sonu Gupta  
**Project**: Interview Accelerator  
**Submission Date**: October 15, 2026  
**Evaluation Track**: AI Product Engineer Intern Challenge  

---

## 1. Submission Deliverables & Links

| Deliverable | Verified Destination | Status |
| :--- | :--- | :---: |
| **Live Deployed Application** | **[`https://interview-accelerator-qt0q.onrender.com`](https://interview-accelerator-qt0q.onrender.com)** | **VERIFIED LIVE** |
| **GitHub Repository** | **[`https://github.com/Guptsonu22/Interview-Accelerator.git`](https://github.com/Guptsonu22/Interview-Accelerator.git)** | **VERIFIED PUSHED** |
| **Project Documentation** | **[`README.md`](README.md)** (Full Architecture, API Reference, Scoring Rubrics) | **VERIFIED UP TO DATE** |
| **Demo Video (Screencast)** | `https://www.loom.com/share/<your-loom-id>` *(or YouTube Unlisted link)* | **RECORDING SCRIPT READY** |
| **Automated Test Suite** | 24/24 Tests Passed (100% pass rate via `pytest -v`) | **VERIFIED CLEAN** |
| **Frontend Production Build** | React 19 + TypeScript + Vite 8 (0 errors, 0 warnings via `oxlint`) | **VERIFIED CLEAN** |

> **Evaluator Quickstart**: Open [`https://interview-accelerator-qt0q.onrender.com`](https://interview-accelerator-qt0q.onrender.com) in Chrome or Edge. Click **"Load Sample Match"** on the landing page, click **"Analyze Job Fit"**, and then click **"Start Interview"** to experience the entire end-to-end pipeline with zero setup or API keys required.

---

## 2. Brief Technical Explanations

### A. Architecture
Interview Accelerator uses a decoupled, production-grade full-stack architecture packaged into a single unified container:
- **Backend**: Built with **FastAPI** (Python 3.11) with asynchronous endpoints, Pydantic v2 data validation schemas, CORS middleware, and global exception handlers. Data persistence is handled by **SQLite** running in **WAL mode** (Write-Ahead Logging) for concurrent read/write isolation without external database overhead.
- **Frontend**: Single-Page Application (SPA) built with **React 19**, **TypeScript**, and **Vite 8**. The UI uses a custom dark-mode glassmorphic design system (`frontend/src/index.css`) with Google Fonts (*Space Grotesk* for technical headings and *Inter* for body readability), animated waveform audio bars, and full keyboard accessibility.
- **Unified Cloud Packaging**: A multi-stage **Dockerfile** builds the React production bundle (`frontend-builder`) and mounts the compiled `dist/` directory directly into FastAPI (`production`). This enables a single container on Render to serve both the static SPA and the `/api/*` endpoints under one domain, eliminating cross-origin complications and cloud latency.

### B. AI / LLM Approach
The AI tier is designed around the **Provider Adapter Pattern** (`backend/services/llm_provider.py`) implementing an abstract `LLMProviderInterface`:
- **Deterministic Offline AI Engine (`DemoProvider`)**: The default active provider. It evaluates candidate answers, computes Job Fit, and generates adaptive follow-ups using heuristic and semantic pattern matching. This guarantees evaluators can test the complete system with sub-second response times, zero network failure risks, and zero reliance on paid API credits.
- **Production Cloud LLM Adapters**: Modular plug-ins for **Google Gemini** (`gemini-2.5-flash`), **OpenAI** (`gpt-4o-mini`), and **Groq** (`llama-3.3-70b-versatile`). Switching requires only setting `LLM_PROVIDER=gemini` or `LLM_PROVIDER=openai` in `.env`.
- **Strict Structured Outputs**: All LLM interactions enforce strict Pydantic JSON schemas (`JobAnalysisResponse`, `CandidateAnalysisResponse`, `JobFitResponse`, `AdaptiveTurnResponse`, `InterviewReportResponse`) to eliminate markdown parsing errors and hallucinations.
- **Security & Prompt Injection Defenses**: The security layer (`backend/core/security.py`) sanitizes text inputs, rejects files >10MB, cleans path traversal characters, and scans for instruction overrides (`ignore previous instructions`, `system prompt:`) before invoking LLM pipelines.

### C. Voice Implementation
The voice pipeline is implemented using the browser-native **Web Speech API**, providing low-latency, client-side audio processing without expensive server-side streaming:
- **Text-to-Speech (TTS - Interviewer Voice)**: Powered by `window.speechSynthesis`. Questions are automatically synthesized with a selected professional voice, natural pitch (1.0), and speaking rate (1.0). Includes controls for **Replay Question**, **Mute / Unmute**, and automated cancellation on screen transitions to prevent audio overlap.
- **Speech-to-Text (STT - Candidate Microphone)**: Powered by `window.webkitSpeechRecognition` / `SpeechRecognition`. Captures candidate speech in continuous mode with interim transcript updates. A live pulsating audio waveform visualizer provides immediate feedback that the microphone is active.
- **Editable Transcript Review Buffer**: Transcribed speech is streamed into an editable text area rather than submitted blindly. Candidates can pause, edit transcription errors, append additional technical context with their keyboard, and submit when ready.
- **Text-Only Fallback**: If audio hardware is missing or browser permissions are denied, the entire application gracefully falls back to keyboard input with zero loss of interview functionality.

### D. Dynamic Questioning Logic
Unlike basic interview bots that read a static list of questions, Interview Accelerator features an **Adaptive Follow-Up State Machine**:
- **3 Progression Levels**:
  1. *Level 1 (Screening)*: Evaluates foundational background, motivation, role alignment, and communication clarity.
  2. *Level 2 (Competency)*: Explores specific technical skills, practical project architectures, and behavioral STAR scenarios.
  3. *Level 3 (Deep-Dive)*: Stress-tests unsupported resume claims, complex failure modes, concurrency bottlenecks, and system trade-offs.
- **10 Adaptive Response Scenarios**: Every candidate response is evaluated against the target competency and routed to a specific follow-up:
  1. *Strong / Detailed Answer* $\rightarrow$ Triggers an **Advanced Scaling Probe** (e.g., 50x load increase, multi-region partitioning).
  2. *Vague / High-Level Answer* $\rightarrow$ Triggers a **Technical Mechanics Probe** (requests specific protocols, serialization formats, cache eviction policies).
  3. *Incorrect Answer* $\rightarrow$ Triggers a **Diagnostic Correction** (identifies the conceptual flaw and asks how to resolve the side effect).
  4. *Candidate Says "I don't know"* $\rightarrow$ Triggers a **Learning Agility Probe** (evaluates foundational first-principles thinking).
  5. *Contradiction with Resume* $\rightarrow$ Triggers a **Scope Verification Probe** (differentiates individual ownership from team contributions).
  6. *Irrelevant / Tangential Answer* $\rightarrow$ Triggers a **Core Competency Refocus** (gently redirects back to the primary engineering question).
  7. *Empty / Minimal Answer* $\rightarrow$ Triggers a **Simplification Entry Point** (breaks the problem into a simpler component).
  8. *Concise & Correct Answer* $\rightarrow$ Triggers an **Edge-Case Edge Probe** (probes race conditions, memory leaks, and failover).
  9. *Partial Answer* $\rightarrow$ Triggers a **Resilience & Fault Tolerance Probe** (asks how unaddressed architectural tiers survive outages).
  10. *Knowledge Gap* $\rightarrow$ Triggers an **Architectural Transition Drill** (guides candidate from single-node to distributed sharding).

### E. Evaluation Methodology
The evaluation system produces transparent, actionable, and mathematically grounded diagnostics:
- **5-Dimension Job Fit Formulation (0–100)**:
  $$\text{Job Fit} = (S_{\text{req}} \times 0.35) + (S_{\text{pref}} \times 0.15) + (P \times 0.20) + (R \times 0.15) + (E \times 0.15)$$
  Every skill is categorized into 🟢 *Matched*, 🟡 *Partial/Emerging*, or 🔴 *Missing Evidence*.
- **7 Core Competency Scores**: Each interview turn evaluates Role Fit (20%), Technical Knowledge (25%), Problem Solving (20%), Communication (10%), Confidence (5%), Depth of Understanding (10%), and Behavioral Fit (10%).
- **Deterministic Readiness Verdict**:
  - **$\ge 85$**: `STRONG CANDIDATE` (Exceeds role criteria, robust technical depth, clear STAR communication)
  - **$70 - 84$**: `INTERVIEW READY` (Meets essential criteria with minor gaps in deep-dive scaling)
  - **$50 - 69$**: `NEEDS PREPARATION` (Foundational knowledge present but lacks hands-on depth or clarity)
  - **$< 50$**: `NOT READY` (Significant competency deficiencies or unverified claims)
- **Question-by-Question Audit Trail**: The final report includes each question asked, the candidate's exact response, the individual turn score, a targeted critique, and a gold-standard **Model STAR Answer**.
- **Personalized 2-Week Preparation Roadmap**: Tailored daily study schedule (Days 1–7 foundational fixes, Days 8–14 advanced mock drills) targeting the candidate's specific identified gaps.
- **Export Formats**: Complete diagnostic reports can be downloaded as standard **Markdown (`.md`)** or printed directly to **PDF**.

### F. Key Technical Decisions
1. **Single Unified Docker Container vs Decoupled Microservices**: By compiling the React frontend in a multi-stage Docker build and serving it via FastAPI's static file handler, we eliminated CORS issues, avoided domain synchronization delays, and ensured the entire platform runs effortlessly under a single free-tier cloud URL.
2. **Local Deterministic Fallback (`DemoProvider`)**: Cloud LLM API keys frequently fail during third-party evaluations due to rate limits or invalid credentials. Implementing an offline heuristic AI engine ensures the application works immediately for any evaluator out-of-the-box.
3. **Web Speech API vs Server-Side Audio Streaming**: Processing audio directly in the candidate's browser eliminates multi-second server transcription latency, saves significant cloud compute bandwidth, and ensures a seamless real-time conversation.
4. **Editable Answer Buffer**: Voice transcription often mishears technical terminology (e.g., "Kubernetes" as "Cooper net is"). Allowing candidates to inspect and edit their spoken words before submission prevents unfair evaluation penalties.
5. **SQLite in WAL Mode**: Lightweight and self-contained with zero external database configuration, yet fully capable of concurrent interview sessions and fast write operations.

---

## 3. How Interview Accelerator Achieves the Final Goal

> *"Build something that makes a candidate think: 'If I can perform well here, I am genuinely prepared for my real interview.'"*

Generic interview prep tools simply generate a list of generic behavioral questions. **Interview Accelerator is built differently:**

1. **It Understands the Job & Candidate First**: Before asking a single question, it cross-references the candidate's resume with the target JD, identifying exact skill matches, weak evidence, and potential resume inflation.
2. **It Tests Real-World Depth**: It doesn't let candidates get away with memorized buzzwords. If a candidate says "I used Redis for caching," the system immediately demands eviction policies, cluster failover mechanics, and data consistency models.
3. **It Mirrors Human Interview Dynamics**: The 3-level progression replicates real hiring loops (Recruiter Screen $\rightarrow$ Technical Competency $\rightarrow$ Architecture Deep-Dive), while the 10 adaptive follow-up branches ensure the interview dynamically responds to the candidate's actual words.
4. **It Provides Immediate, Actionable Remediation**: Instead of a generic "Good job", the candidate receives model STAR answers demonstrating how a senior engineer would answer, alongside a structured 2-week daily study roadmap to close their exact gaps before the real interview.

---

## 4. Complete User Journey Demo Script (For Video Screencast)

| Scene | Duration | Screen Action | Voiceover Narrative |
| :---: | :---: | :--- | :--- |
| **1. Intro** | 0:00 – 0:30 | Home screen at `interview-accelerator-qt0q.onrender.com` | *"Hello, I am Sonu Gupta, presenting Interview Accelerator for EDXSO Assignment 3. The platform solves the problem of under-evidenced candidates by grounding interview rounds in target job descriptions, candidate resumes, and dynamic follow-up questioning."* |
| **2. Intake & Job Fit** | 0:30 – 1:15 | Click **"Load Sample Match"** $\rightarrow$ Click **"Analyze Job Fit"** | *"Here we ingest a Senior Systems Engineer JD and candidate resume. The platform computes a transparent 5-dimension Job Fit score (84/100), categorizing competencies into Matched, Partial, and Missing evidence using zero external API dependencies."* |
| **3. Voice & Adaptive Follow-Up** | 1:15 – 2:45 | Click **"Start Interview"** $\rightarrow$ Click **🔊 Replay** $\rightarrow$ Click **🎙️ Speak Answer** | *"Entering Level 2 Competency round. Notice the interviewer speaks the question via TTS. I speak my answer, which streams into an editable review buffer. When I submit a strong answer about distributed caching, the engine immediately adapts with a 50x scaling probe."* |
| **4. Adaptive Scenarios** | 2:45 – 3:30 | Submit a vague answer $\rightarrow$ Show mechanics probe | *"Notice how the interviewer shifts: when an answer lacks detail, it probes technical mechanics; if an answer contains misconceptions, it offers diagnostic guidance. We support all 3 levels from Screening to Deep-Dive."* |
| **5. Report & Export** | 3:30 – 4:00 | Click **"Finish Interview"** $\rightarrow$ Show Report Screen $\rightarrow$ Click **Download Markdown** | *"Here is the final diagnostic report: overall score, 7 competency radar breakdowns, question-level model STAR answers, and a prioritized 2-week study roadmap. Candidates can export this report as Markdown or print to PDF."* |
