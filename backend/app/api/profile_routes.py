"""
FastAPI REST API Routes for Personalization & Learner Model (Agent 3)
Conforming strictly to Sections 9, 10, 21, 23, 25, 38, 39, 40.
"""

from typing import Optional, Dict, Any, List
from fastapi import APIRouter, HTTPException, Query

from backend.personalization.schemas import (
    StudentProfile, PersonalizationContext, LearningHistoryEntry,
    AssessmentHistoryEntry, LearnerKnowledge, CreateProfileRequest,
    UpdateProfileRequest, KnowledgeUpdateEvidence, ResetProfileRequest
)
from backend.personalization.service import personalization_service

router = APIRouter(prefix="/students", tags=["Learner Personalization & Profile"])

@router.post("/profile", response_model=StudentProfile)
async def create_or_initialize_profile(payload: CreateProfileRequest):
    """
    Creates or initializes a student profile.
    If profile already exists, updates only explicitly provided fields
    without deleting historical learning or mastery data.
    """
    try:
        profile = personalization_service.create_or_update_profile(payload)
        return profile
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create profile: {str(e)}")

@router.get("/{student_id}/profile", response_model=StudentProfile)
async def get_student_profile(student_id: str):
    """Retrieves full student profile including preferences, mastery, and history."""
    profile = personalization_service.get_profile(student_id)
    if not profile:
        raise HTTPException(status_code=404, detail=f"Student '{student_id}' not found")
    return profile

@router.patch("/{student_id}/profile", response_model=StudentProfile)
async def patch_student_profile(student_id: str, updates: UpdateProfileRequest):
    """
    Safe partial update of student profile / preferences.
    Guaranteed not to overwrite or wipe learning history, mastery, or misconceptions.
    """
    updated = personalization_service.update_profile(student_id, updates)
    if not updated:
        raise HTTPException(status_code=404, detail=f"Student '{student_id}' not found")
    return updated

@router.get("/{student_id}/learning-context", response_model=PersonalizationContext)
async def get_learning_context(
    student_id: str,
    topic: Optional[str] = Query(None, description="Current lesson topic to filter knowledge"),
    level: Optional[str] = Query(None, description="Explicit session level override"),
    language: Optional[str] = Query(None, description="Explicit session language override"),
    style: Optional[str] = Query(None, description="Explicit session teaching style override"),
    depth: Optional[str] = Query(None, description="Explicit session depth override"),
    duration: Optional[float] = Query(None, description="Explicit session duration in minutes")
):
    """
    Returns COMPACT, actionable personalization context intended for Agent 1 (Teaching Brain).
    Applies 5-tier priority conflict resolution and actionable constraint generation.
    """
    # Build dynamic session request object from query overrides if provided
    request_mock = None
    if any([level, language, style, depth, duration, topic]):
        class RequestMock:
            pass
        req = RequestMock()
        req.topic = topic
        req.educational_level = level
        req.preferred_language = language
        req.teaching_style = style
        req.desired_depth = depth
        req.available_time_minutes = duration
        request_mock = req

    context = personalization_service.get_personalization_context(
        student_id=student_id,
        topic=topic,
        request=request_mock
    )
    return context

@router.get("/{student_id}/history", response_model=List[LearningHistoryEntry])
async def get_student_history(
    student_id: str,
    limit: int = Query(10, ge=1, le=100)
):
    """Retrieves recent learning history sessions for the student."""
    return personalization_service.get_recent_learning_history(student_id, limit=limit)

@router.get("/{student_id}/topic/{topic}/knowledge", response_model=Dict[str, LearnerKnowledge])
async def get_topic_knowledge(student_id: str, topic: str):
    """Retrieves concept mastery states filtered for a specific topic."""
    all_knowledge = personalization_service.repository.get_knowledge_state(student_id)
    relevant_ids = personalization_service.engine._get_relevant_concept_ids(topic)
    if not relevant_ids:
        # If no strict domain mapping, return concepts whose name matches the topic
        t_norm = topic.lower().replace(" ", "_")
        return {k: v for k, v in all_knowledge.items() if t_norm in k.lower()}
    return {k: v for k, v in all_knowledge.items() if personalization_service.engine._is_concept_relevant(k, relevant_ids)}

@router.post("/{student_id}/knowledge/update", response_model=LearnerKnowledge)
async def update_concept_knowledge_endpoint(
    student_id: str,
    concept_id: str = Query(..., description="Concept to update"),
    payload: KnowledgeUpdateEvidence = ...
):
    """
    Endpoint for Agent 6 (Response Evaluator) to submit in-lesson evidence.
    Updates concept mastery score, confidence, attempts, and tracks misconceptions.
    """
    try:
        updated = personalization_service.update_concept_knowledge(
            student_id=student_id,
            concept_id=concept_id,
            evidence=payload
        )
        return updated
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update knowledge: {str(e)}")

@router.post("/{student_id}/assessment/update", response_model=AssessmentHistoryEntry)
async def update_assessment_endpoint(
    student_id: str,
    payload: AssessmentHistoryEntry
):
    """
    Endpoint for Agent 7 (Assessment Engine) to record assessment results.
    Updates concept mastery scores, updates strong/weak concepts, and appends to history.
    """
    try:
        recorded = personalization_service.record_assessment_result(
            student_id=student_id,
            assessment_data=payload
        )
        return recorded
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to record assessment: {str(e)}")

@router.post("/{student_id}/reset")
async def reset_student_profile(
    student_id: str,
    payload: ResetProfileRequest
):
    """
    Granular reset endpoint (Section 40).
    Supported options: RESET_PREFERENCES, RESET_KNOWLEDGE, RESET_HISTORY, RESET_ALL.
    """
    success = personalization_service.reset_profile(student_id, payload.reset_type)
    if not success:
        raise HTTPException(status_code=400, detail="Reset operation failed or student not found")
    return {"status": "success", "reset_type": payload.reset_type, "student_id": student_id}
