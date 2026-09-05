# Deployment & Setup Guide

**Project:** AI Teacher: Build a Human-Like AI Educator That Teaches Through Video  
**Target Environment:** Windows 10/11, macOS, or Linux (Ubuntu 22.04+)  
**Runtime:** Python 3.10+ & Node.js 18+

---

## 1. Prerequisites

Ensure the following tools are installed on the host system:
- **Python:** Version `3.10` or higher (`python --version`)
- **Node.js:** Version `18.x` or higher (`node -v`)
- **npm:** Version `9.x` or higher (`npm -v`)
- **Git:** Standard git client

---

## 2. Environment Configuration

1. In the repository root, copy the `.env.example` template:
   ```bash
   # Windows PowerShell / CMD
   copy .env.example .env

   # Linux / macOS
   cp .env.example .env
   ```

2. Configure runtime parameters (optional):
   - **`GEMINI_API_KEY`**: (Optional) Provide a Google Gemini API key to enable live LLM generation for arbitrary new topics. If left blank, the application operates in **Deterministic Mock Mode** with 100% functionality for all STEM curricula and hackathon scenarios.
   - **`ENABLE_MOCK_PROVIDERS`**: Set to `true` (default) to ensure uninterrupted fallback.
   - **`DEMO_MODE`**: Set to `true` (default) for preloaded 1-click canonical testing.
   - **`MAX_RETEACH_ATTEMPTS`**: Set to `2` (default) for adaptive loop protection.

---

## 3. Backend Installation & Startup

1. Open a terminal and navigate to the project directory:
   ```bash
   cd "d:/Project and Related Files/third YEAR/AI-teacher"
   ```

2. Install Python dependencies:
   ```bash
   pip install -r backend/requirements.txt
   ```

3. Initialize the database directory (automatically created on first boot if missing):
   ```bash
   # The SQLite database is automatically initialized at backend/data/learner_profiles.db
   ```

4. Start the FastAPI backend service:
   ```bash
   python backend/run_backend.py
   ```
   - **Backend API Base:** `http://127.0.0.1:8000`
   - **Interactive OpenAPI Docs:** `http://127.0.0.1:8000/docs`
   - **System Health Endpoint:** `http://127.0.0.1:8000/health`

---

## 4. Frontend Installation & Startup

1. Open a separate terminal and navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install Node dependencies (if not already installed):
   ```bash
   npm install
   ```

3. Start the Vite development server:
   ```bash
   npm run dev
   ```
   - **Frontend UI:** `http://localhost:5173`

---

## 5. One-Click Hackathon Launch (Windows)

For convenience during demonstrations, run the included batch launcher from the root directory:
```powershell
.\start.bat
```
This automatically launches both the backend and frontend in separate processes and opens the relevant URLs.

---

## 6. Verifying System Health

Run a GET request against the health check endpoint:
```bash
curl http://127.0.0.1:8000/health
```

Expected Response:
```json
{
  "status": "ok",
  "service": "AI Teacher - Human-Like Adaptive AI Educator",
  "version": "1.0.0",
  "environment": "development",
  "demo_mode": true,
  "subsystems": {
    "orchestrator": "active",
    "rag": "ready",
    "personalization_db": "connected",
    "evaluation_engine": "active",
    "adaptation_engine": "active",
    "assessment_engine": "active",
    "llm_provider": "deterministic_mock_ready",
    "voice_provider": "web_speech_api",
    "avatar_provider": "svg_animated"
  }
}
```

---

## 7. Running the Automated Test Suite

To verify all 54 unit, integration, and end-to-end tests:
```bash
python -m pytest backend/tests -v
```
All tests should pass with code `0`.

---

## 8. Production Considerations

- **Reverse Proxy:** In production, route requests through NGINX or Caddy with SSL/TLS termination.
- **ASGI Process Manager:** Deploy Uvicorn workers behind Gunicorn:
  ```bash
  gunicorn -w 4 -k uvicorn.workers.UvicornWorker backend.app.main:app --bind 0.0.0.0:8000
  ```
- **Static Assets:** Build the production frontend bundle via `npm run build` and serve the `dist/` directory via CDN or NGINX.
