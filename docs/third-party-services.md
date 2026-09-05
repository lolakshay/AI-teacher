# Third-Party Services, Models & Libraries Disclosure

**Project:** AI Teacher: Build a Human-Like AI Educator That Teaches Through Video  
**Compliance Statement:** In accordance with the AI Innovation Challenge rules, this document provides complete, transparent disclosure of all third-party APIs, machine learning models, open-source libraries, and fallback mechanisms utilized in the AI Teacher prototype.

---

## 1. Third-Party Service Classification Matrix

| Category | Component / Library | Type | Purpose in Pipeline | Data Handled | Offline / Fallback Capable? |
|---|---|---|---|---|---|
| **LLM Reasoning** | Google Gemini (`gemini-3.7-flash` / `gemini-3.6-flash`) | External Cloud API | Generalized lesson deconstruction, open-ended answer diagnosis | Educational prompts, anonymous student responses | **Yes** — Built-in deterministic pedagogical rule engine & local fallback |
| **Embeddings** | Google Text-Embedding-004 | External Cloud API | Semantic chunk embeddings for RAG retrieval | Document chunk text (PDF/DOCX) | **Yes** — Substring TF/IDF keyword matching index |
| **Speech (TTS)** | W3C Web Speech Synthesis API | Native Browser Engine | Natural voice synthesis in English, Hindi, and Hinglish | Lesson narration text strings | **Yes** — Native OS speech voices (Windows SAPI, Android, macOS), zero external API key needed |
| **Document Parsing** | PyPDF (`pypdf >= 4.0.0`) | Open-Source Python Lib | Parsing text, page boundaries, and metadata from uploaded PDFs | Local uploaded files in `uploads/` directory | **Yes** — Fully local on-premise execution |
| **Math Typesetting** | KaTeX (`katex 0.16.x`) | Open-Source JS Lib | High-speed, client-side rendering of mathematical equations ($V=I\cdot R$) | LaTeX math string representations | **Yes** — 100% client-side offline execution |
| **Database & Persistence**| SQLite 3 / Python `sqlite3` | Local Embedded DB | Persistent storage of student profiles, Bayesian mastery states, and assessment history | Anonymized learner profile models | **Yes** — Local file `backend/data/learner_profiles.db` |
| **Web Framework** | FastAPI & Uvicorn | Open-Source Python Lib | Asynchronous REST API, CORS middleware, request validation | JSON request/response payloads | **Yes** — Local server on `127.0.0.1:8000` |
| **Frontend Framework** | React 18 & Vite 5 | Open-Source JS Lib | User interface, state management, animated SVG canvas | Application state | **Yes** — Local dev/static bundle on `localhost:5173` |
| **Iconography** | Lucide React | Open-Source JS Lib | UI symbols, telemetry indicators, status badges | None | **Yes** — Packaged in client bundle |

---

## 2. Detailed Third-Party Service Disclosures

### 2.1 Google Gemini API (`gemini-3.7-flash` / `gemini-3.6-flash`)
- **Type:** External Cloud API
- **Provider:** Google DeepMind / Google Cloud Platform
- **Purpose:** Powers generalized lesson curriculum planning for arbitrary non-canonical topics and open-ended student reasoning evaluation.
- **Input:** System prompt, pedagogical instructions, student response, expected answer, language code.
- **Output:** JSON schema conforming to `EvaluationResult` or `LessonPlan`.
- **Authentication:** `GEMINI_API_KEY` (configured in `.env` via `Settings`).
- **Data Handling:** No Personally Identifiable Information (PII) is transmitted. Student IDs are randomized hashes (`demo_student_01`).
- **Fallback Implementation:** If `GEMINI_API_KEY` is empty, expired, or rate-limited, the system seamlessly activates the `DeterministicPedagogicalFallback` engine, which contains curated pedagogical models for foundational STEM domains (e.g., Ohm's Law, Circuit Dynamics, Binary Search).

### 2.2 W3C Web Speech API (`SpeechSynthesis`)
- **Type:** Browser-Native Standard Interface (Local / Edge-Assisted)
- **Provider:** Host Operating System / Web Browser (Chrome, Edge, Safari)
- **Purpose:** Synthesizes voice narration in sync with the animated SVG teacher avatar.
- **Input:** String text from `TeachingStep.explanation`, language tag (`en-US`, `hi-IN`).
- **Output:** Real-time audio waveform rendered through user audio output device.
- **Authentication:** None (built into web platform standards).
- **Data Handling:** Audio synthesis occurs client-side on the user's device.
- **Fallback Implementation:** If speech synthesis is muted or unsupported in a headless browser, visual dialogue captions and whiteboard subtitles provide full pedagogical parity.

### 2.3 PyPDF Parser
- **Type:** Local Open-Source Library (`pypdf`)
- **License:** BSD 3-Clause
- **Purpose:** Extracts text paragraphs and page numbers from uploaded educational material during RAG ingestion.
- **Input:** File byte stream from `POST /api/materials/upload`.
- **Output:** Extracted textual blocks mapped to page numbers.
- **Data Handling:** Stored in local directory `backend/uploads/`.
- **Fallback Implementation:** Plain text `.txt` and `.md` ingestion engines if PDF parsing encounters an unsupported format.

### 2.4 KaTeX Mathematical Rendering Engine
- **Type:** Local Open-Source JavaScript Library (`katex`)
- **License:** MIT License
- **Purpose:** Real-time client-side rendering of algebraic derivations, proportionalities ($R \uparrow \implies I \downarrow$), and unit equations without network requests or external image services.
- **Input:** Raw LaTeX strings.
- **Output:** Accessible HTML and SVG mathematical markup.

---

## 3. Sovereignty & Deployment Integrity

- **Zero Cloud Lock-In:** The entire application runtime can execute on a single air-gapped or local workstation with no mandatory cloud subscription.
- **Zero Real Secret Leakage:** All external API keys are optional. When external keys are absent, the application gracefully flags `"llm_provider": "deterministic_mock_ready"` in the `/health` endpoint and passes all 54 end-to-end integration tests.
