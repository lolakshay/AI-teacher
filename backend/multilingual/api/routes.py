"""
FastAPI REST API Routes for Agent 8: Multilingual Teaching Engine.
Conforms strictly to Section 37 and Section 42.
"""

from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Query, Body
from pydantic import BaseModel, Field

from backend.multilingual.models.language import (
    SUPPORTED_LANGUAGES,
    LanguageConfig,
    normalize_language_code,
    is_supported_language
)
from backend.multilingual.models.adaptation import (
    LanguageAdaptationRequest,
    LanguageSwitchRequest,
    LanguageSwitchResult,
    VisualTextLocalization,
    LanguageDetectionResult,
    ValidationResult
)
from backend.multilingual.models.localized_step import LocalizedTeachingStep
from backend.multilingual.models.errors import MultilingualException
from backend.multilingual.services.translation_service import translation_service
from backend.multilingual.services.language_service import language_service
from backend.multilingual.services.validation_service import validation_service
from backend.multilingual.services.cache_service import cache_service
from backend.app.core.models import TeachingStep

router = APIRouter(prefix="/language", tags=["Multilingual Teaching Engine"])

# Request payload schemas
class TextDetectionPayload(BaseModel):
    text: str = Field(..., min_length=1)

class VisualLabelsPayload(BaseModel):
    labels: List[str]
    target_language: str = "hi"

class ValidationPayload(BaseModel):
    source_text: str
    adapted_text: str
    required_terms: Optional[List[str]] = None
    source_concept_id: Optional[str] = None
    adapted_concept_id: Optional[str] = None

@router.get("/supported", response_model=Dict[str, LanguageConfig])
async def get_supported_languages():
    """Returns officially supported languages, scripts, and teaching modes."""
    return SUPPORTED_LANGUAGES

@router.post("/adapt")
async def adapt_text(request: LanguageAdaptationRequest):
    """
    Adapts educational text from source language to target teaching language
    while preserving formulas, units, code, and technical terminology.
    """
    try:
        result = translation_service.adapt_text(request)
        return result
    except MultilingualException as me:
        raise HTTPException(status_code=400, detail=me.to_dict())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Adaptation failed: {str(e)}")

@router.post("/teaching-step", response_model=LocalizedTeachingStep)
async def adapt_teaching_step(
    step: TeachingStep = Body(...),
    target_language: str = Query("hi", description="Target teaching language (hi, hi-en, en)")
):
    """
    Localizes an entire TeachingStep for downstream consumption by Agent 4 (Video)
    and Agent 5 (Voice). Concept ID remains invariant.
    """
    try:
        localized = translation_service.adapt_teaching_step(
            step=step,
            target_language=target_language
        )
        return localized
    except MultilingualException as me:
        raise HTTPException(status_code=400, detail=me.to_dict())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Teaching step localization failed: {str(e)}")

@router.post("/detect", response_model=LanguageDetectionResult)
async def detect_language(payload: TextDetectionPayload):
    """Detects whether text is English, Hindi (Devanagari), or Hinglish (mixed Latin)."""
    try:
        result = language_service.detect_language(payload.text)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Language detection failed: {str(e)}")

@router.post("/switch", response_model=LanguageSwitchResult)
async def switch_language(payload: LanguageSwitchRequest):
    """
    Switches active teaching language for a session WITHOUT restarting the lesson.
    Topic, concept, progress, evaluations, and misconceptions remain intact.
    """
    try:
        result = language_service.switch_session_language(
            session_id=payload.session_id,
            target_language=payload.target_language,
            teaching_style=payload.teaching_style
        )
        return result
    except MultilingualException as me:
        raise HTTPException(status_code=404 if me.code == "CONTEXT_MISSING" else 400, detail=me.to_dict())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Language switch failed: {str(e)}")

@router.post("/visual-labels", response_model=List[VisualTextLocalization])
async def localize_visual_labels(payload: VisualLabelsPayload):
    """Provides localized visual labels for Agent 4 video engine."""
    try:
        return translation_service.localize_visual_labels(
            labels=payload.labels,
            target_language=payload.target_language
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Visual label localization failed: {str(e)}")

@router.post("/validate", response_model=ValidationResult)
async def validate_content(payload: ValidationPayload):
    """Validates preservation of formulas, numbers, units, code, and concept IDs."""
    try:
        return validation_service.validate_adaptation(
            source_text=payload.source_text,
            adapted_text=payload.adapted_text,
            required_terms=payload.required_terms,
            source_concept_id=payload.source_concept_id,
            adapted_concept_id=payload.adapted_concept_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Validation failed: {str(e)}")

@router.get("/cache/stats")
async def get_cache_stats():
    """Returns translation cache statistics."""
    return cache_service.stats()
