"""
Localized Teaching Step and Question Data Contracts.
These contracts are consumed downstream by Agent 4 (Video Composition)
and Agent 5 (Voice Synthesis) while preserving canonical concept identity.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class LocalizedQuestion(BaseModel):
    question_id: str = Field(..., description="Canonical question identifier")
    canonical_text: str = Field(..., description="Language-neutral canonical source text")
    localized_text: str = Field(..., description="Localized prompt for learner")
    language: str = Field(..., description="Language of localized question")
    expected_concept: str = Field(..., description="Language-neutral target concept (e.g. 'inverse_relationship')")
    options: Optional[List[str]] = None
    hints: List[str] = Field(default_factory=list)
    question_type: str = "conceptual_check"
    pedagogical_goal: Optional[str] = None

class LocalizedVisualInstruction(BaseModel):
    type: str = Field(..., description="Visual type: circuit, math_derivation, code_trace, diagram")
    title: str = Field(..., description="Localized visual title")
    caption: str = Field(default="", description="Localized caption")
    labels: Dict[str, str] = Field(
        default_factory=dict,
        description="Mapping of canonical labels to localized labels for Agent 4"
    )
    data: Dict[str, Any] = Field(
        default_factory=dict,
        description="Preserved numerical/structural payload (formulas, numerical values, graph nodes)"
    )

class LocalizedTeachingStep(BaseModel):
    teaching_step_id: str = Field(..., description="Teaching step ID")
    concept_id: str = Field(..., description="Language-neutral concept identifier (invariant across translations)")
    source_language: str = Field(default="en", description="Source document/explanation language")
    teaching_language: str = Field(..., description="Active presentation language (e.g. 'hi', 'hi-en', 'en')")

    canonical_text: str = Field(..., description="Canonical source explanation")
    spoken_text: str = Field(..., description="Natural spoken script prepared for Agent 5 TTS voice")
    display_text: str = Field(..., description="Screen text prepared for Agent 4 video rendering")

    example: Optional[str] = None
    terminology: List[str] = Field(default_factory=list, description="Preserved or highlighted technical terms")
    visual_instruction: Optional[LocalizedVisualInstruction] = None
    question: Optional[LocalizedQuestion] = None
    source_references: List[Dict[str, Any]] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class LocalizedAssessmentQuestion(BaseModel):
    question_id: str = Field(..., description="Canonical assessment question identifier")
    canonical_text: str = Field(..., description="Canonical assessment prompt")
    localized_text: str = Field(..., description="Localized question prompt")
    language: str = Field(..., description="Target teaching language")
    expected_concept: str = Field(..., description="Target concept ID for Agent 7 grading and Agent 3 mastery tracking")
    expected_answer: Optional[str] = None
    options: Optional[List[str]] = None
    hints: List[str] = Field(default_factory=list)
