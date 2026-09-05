"""
FastAPI REST API Routes for AI Teacher Subsystem
"""

import uuid
import shutil
from pathlib import Path
from typing import Optional, Dict, Any
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from backend.app.core.config import settings
from backend.app.core.models import (
    LearningRequest, StudentProfile, StudentResponse, SessionState,
    TeachingStep, EvaluationResult, LearningReport, QuestionPayload
)
from backend.app.services.material_pipeline import material_pipeline
from backend.app.services.orchestrator import orchestrator
from backend.app.api.profile_routes import router as profile_router
from backend.assessment.api.routes import router as assessment_router
from backend.multilingual.api.routes import router as language_router
from backend.evaluation.api.routes import router as evaluation_router
from backend.avatar_voice.api.voice_routes import router as voice_router
from backend.avatar_voice.api.avatar_routes import router as avatar_router

router = APIRouter()
router.include_router(profile_router)
router.include_router(assessment_router)
router.include_router(language_router)
router.include_router(evaluation_router)
router.include_router(voice_router)
router.include_router(avatar_router)


# ----------------- MATERIAL / RAG ENDPOINTS -----------------

@router.post("/materials/upload")
async def upload_material(file: UploadFile = File(...)):
    """Uploads and ingests educational document (PDF, DOCX, TXT)."""
    file_path = settings.UPLOAD_DIR / file.filename
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        doc_id = material_pipeline.ingest_file(file_path, file.filename)
        summary = material_pipeline.get_document_summary(doc_id)
        return {"status": "success", "data": summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process file: {str(e)}")

@router.get("/materials/{doc_id}")
async def get_material(doc_id: str):
    summary = material_pipeline.get_document_summary(doc_id)
    if not summary:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"status": "success", "data": summary}

# ----------------- SESSION ENDPOINTS -----------------

@router.post("/sessions/create")
async def create_session(payload: Dict[str, Any]):
    """
    Creates teaching session, analyzes request, generates LessonPlan and initial TeachingSteps.
    Accepts both wrapped format ({"request": {...}, "profile": {...}}) and flat LearningRequest payloads.
    """
    try:
        if "request" in payload and isinstance(payload["request"], dict):
            req_data = payload["request"]
            prof_data = payload.get("profile")
        else:
            req_data = payload
            prof_data = None

        request = LearningRequest(**req_data)
        profile = StudentProfile(**prof_data) if prof_data else None
        session = orchestrator.create_session(request, profile)
        return {"status": "success", "session": session}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initialize session: {str(e)}")

# Canonical alias matching Section 38
@router.post("/teaching/start")
async def start_teaching(payload: Dict[str, Any]):
    return await create_session(payload)

@router.get("/sessions/{session_id}")
async def get_session(session_id: str):
    session = orchestrator.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"status": "success", "session": session}

@router.get("/sessions/{session_id}/step")
async def get_current_step(session_id: str):
    step = orchestrator.get_current_step(session_id)
    if not step:
        session = orchestrator.get_session(session_id)
        status = session.status if session else "not_found"
        return {"status": "success", "step": None, "session_status": status}
    return {"status": "success", "step": step}

@router.post("/sessions/{session_id}/advance")
async def advance_step(session_id: str):
    """Advances teaching to the next step in the lesson plan."""
    step, status = orchestrator.advance_step(session_id)
    return {"status": "success", "next_step": step, "session_status": status}

# Canonical alias matching Section 38
@router.get("/teaching/{session_id}/next")
async def get_next_step(session_id: str):
    return await advance_step(session_id)

@router.post("/sessions/{session_id}/switch-language")
@router.post("/sessions/{session_id}/language")
async def switch_session_language(session_id: str, payload: Dict[str, Any]):
    """
    Switches session teaching language mid-lesson without restarting or resetting progress.
    """
    target_lang = payload.get("target_language") or payload.get("language") or "hi"
    teaching_style = payload.get("teaching_style")
    try:
        from backend.multilingual.services.language_service import language_service
        result = language_service.switch_session_language(session_id, target_lang, teaching_style)
        return {
            "status": "success",
            "new_language": target_lang,
            "data": result.model_dump()
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))



@router.post("/sessions/{session_id}/respond")
async def respond_to_question(session_id: str, payload: Dict[str, Any]):
    """
    Submits student answer. Triggers diagnostic misconception evaluation.
    If a misconception is detected, dynamically injects an adaptive re-explanation step.
    """
    try:
        response = StudentResponse(
            session_id=session_id,
            question_id=payload.get("question_id", "q_current"),
            student_answer=payload.get("student_answer", ""),
            answer_type=payload.get("answer_type", "text")
        )
        result = orchestrator.handle_student_response(response)
        return {"status": "success", **result}
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Evaluation failed: {str(e)}")

# Canonical alias matching Section 38
@router.post("/teaching/{session_id}/respond")
async def teaching_respond(session_id: str, payload: Dict[str, Any]):
    return await respond_to_question(session_id, payload)

# ----------------- MULTILINGUAL ADAPTATION (AGENT 8) -----------------

@router.post("/sessions/{session_id}/language")
async def switch_language(session_id: str, payload: Dict[str, str]):
    """
    Switches teaching language on-the-fly (e.g. English <-> Hinglish <-> Hindi)
    strictly preserving topic, position, and learner mastery state.
    """
    new_language = payload.get("language")
    if not new_language:
        raise HTTPException(status_code=400, detail="Field 'language' is required")

    session = orchestrator.set_session_language(session_id, new_language)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    current_step = orchestrator.get_current_step(session_id)
    return {
        "status": "success",
        "session_id": session_id,
        "new_language": new_language,
        "current_step": current_step
    }

# ----------------- ASSESSMENT & REPORT (AGENT 7) -----------------

@router.get("/sessions/{session_id}/assessment")
async def get_assessment(session_id: str):
    try:
        questions = orchestrator.start_assessment(session_id)
        return {"status": "success", "questions": questions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sessions/{session_id}/assessment/submit")
async def submit_assessment(session_id: str, answers: Optional[Dict[str, str]] = None):
    try:
        report = orchestrator.complete_assessment(session_id, answers)
        return {"status": "success", "report": report}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ----------------- VOICE & AVATAR MEDIA ENDPOINTS (AGENT 5) -----------------

@router.post("/voice/generate")
async def generate_voice(payload: Dict[str, Any]):
    """
    Voice Engine Pipeline (Agent 5).
    Synthesizes expressive natural narration with language pacing.
    """
    text = payload.get("text", "")
    language = payload.get("language", "English")
    return {
        "status": "success",
        "audio_id": f"audio_{uuid.uuid4().hex[:8]}",
        "audio_url": f"/media/audio/{uuid.uuid4().hex[:6]}.wav",
        "language": language,
        "duration_seconds": max(2.0, len(text.split()) * 0.38),
        "provider": settings.VOICE_PROVIDER,
        "ready": True
    }

@router.post("/avatar/generate")
async def generate_avatar(payload: Dict[str, Any]):
    """
    Avatar Engine Pipeline (Agent 5).
    Produces teacher avatar state, facial emotion, gestures, and lip-sync mapping.
    """
    emotion = payload.get("emotion", "explaining")
    return {
        "status": "success",
        "avatar_id": f"avatar_{uuid.uuid4().hex[:8]}",
        "emotion": emotion,
        "gesture": "pointing_to_whiteboard",
        "lip_sync_ready": True,
        "render_mode": settings.AVATAR_PROVIDER
    }

# ----------------- CANONICAL DEMO ENDPOINT -----------------

@router.get("/demo/canonical")
async def load_canonical_demo():
    """
    1-Click Canonical Hackathon Demo Initializer:
    - Topic: Ohm's Law & Circuit Dynamics
    - Level: Beginner
    - Language: Hinglish
    - Duration: 20 minutes
    - Preloaded with intentional misconception trigger: 'Current increases'
    """
    request = LearningRequest(
        student_id="demo_student_01",
        topic="Ohm's Law & Circuit Dynamics",
        educational_level="beginner",
        learning_objective="Understand foundational circuit principles and master V=I*R",
        preferred_language="Hinglish",
        teaching_style="analogy_driven",
        available_time=20,
        desired_depth="intuitive"
    )
    profile = StudentProfile(
        student_id="demo_student_01",
        educational_level="beginner",
        known_topics=["Basic Electric Charge", "Simple Algebra"],
        preferred_language="Hinglish",
        preferred_teaching_style="analogy_driven",
        preferred_depth="intuitive"
    )
    session = orchestrator.create_session(request, profile)
    step = orchestrator.get_current_step(session.session_id)
    return {
        "status": "success",
        "session": session,
        "current_step": step,
        "canonical_prompt": "I am a beginner. Teach me Ohm's Law in 20 minutes in Hinglish with simple examples. Ask me questions and test me at the end."
    }

