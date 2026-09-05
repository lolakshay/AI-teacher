"""
Adaptation, Language Switching, Validation, and Detection Contracts.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class LanguageAdaptationRequest(BaseModel):
    session_id: Optional[str] = None
    teaching_step_id: Optional[str] = None
    source_text: str = Field(..., min_length=1, description="Source educational text to adapt")
    source_language: str = Field(default="en", description="Source text language (e.g., 'en', 'hi')")
    target_language: str = Field(default="hi", description="Requested teaching language (e.g., 'hi', 'hi-en', 'en')")
    topic: Optional[str] = Field(None, description="Current lesson topic (e.g., 'Ohm\\'s Law')")
    concept_id: Optional[str] = Field(None, description="Language-neutral concept identifier (e.g., 'inverse_relationship')")
    learner_level: str = Field(default="beginner", description="Learner level: beginner, intermediate, advanced")
    teaching_style: str = Field(default="analogy_driven", description="Teaching style: simple, analogy_driven, technical, conversational, exam-focused")
    preserve_terminology: bool = Field(default=True, description="Enforce preservation of domain terms")
    terminology_hints: List[str] = Field(default_factory=list, description="Explicit terms to preserve/guide")
    metadata: Dict[str, Any] = Field(default_factory=dict)

class LanguageSwitchRequest(BaseModel):
    session_id: str = Field(..., description="Active session ID")
    target_language: str = Field(..., description="Language to switch to (e.g., 'hi', 'hi-en', 'en')")
    teaching_style: Optional[str] = Field(None, description="Optional override for teaching style")
    preserve_progress: bool = Field(default=True, description="Strictly invariant - must remain True")

class LanguageSwitchResult(BaseModel):
    session_id: str
    previous_language: str
    current_language: str
    current_concept: str
    lesson_position: int
    total_steps: int
    localized_current_step: Optional[Dict[str, Any]] = None
    status: str = "success"
    message: str = "Language switched successfully with full context preserved"

class VisualTextLocalization(BaseModel):
    source: str = Field(..., description="Original visual label")
    localized: str = Field(..., description="Localized visual label")
    preserve_original: bool = True
    caption: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class LanguageDetectionResult(BaseModel):
    language: str = Field(..., description="Detected canonical language code")
    confidence: float = Field(..., ge=0.0, le=1.0)
    script: str = Field(default="Latin")
    is_mixed: bool = False
    detected_markers: List[str] = Field(default_factory=list)

class ValidationResult(BaseModel):
    is_valid: bool = True
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    formulas_preserved: bool = True
    numbers_preserved: bool = True
    units_preserved: bool = True
    code_preserved: bool = True
    terms_preserved: bool = True
    concept_id_preserved: bool = True
    retryable: bool = False
