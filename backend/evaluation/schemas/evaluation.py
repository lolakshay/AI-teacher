"""
Evaluation Result Schemas for Agent 6.
Conforms to Sections 6, 7, 8, 9, 10, 11, 12, 13, 35, 36, 37, 51, 52.
"""

from typing import List, Optional, Literal
from pydantic import BaseModel, Field
import uuid

EvaluationClassification = Literal[
    "correct",            # 0.85 - 1.00
    "mostly_correct",     # 0.60 - 0.84
    "partially_correct",  # 0.30 - 0.59
    "incorrect",          # 0.00 - 0.29
    "ambiguous",          # Unclear / cannot evaluate reliably
    "no_answer",          # "I don't know", "skip", empty
]

MisconceptionType = Literal[
    "definition_confusion",
    "formula_confusion",
    "sign_error",
    "unit_confusion",
    "proportionality_confusion",
    "inverse_relationship_confusion",
    "cause_effect_confusion",
    "prerequisite_gap",
    "process_order_confusion",
    "terminology_confusion",
    "conceptual_overgeneralization",
    "calculation_error",
    "reasoning_error",
    "unknown",
]

EvaluationStatus = Literal[
    "success",
    "ambiguous",
    "insufficient_context",
    "unavailable",
]


class MisconceptionDetails(BaseModel):
    detected: bool = False
    type: Optional[MisconceptionType] = None
    description: Optional[str] = None
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)


class EvaluationResult(BaseModel):
    """
    Strongly structured evaluation result.
    Consumed by Agent 1 (Orchestrator), Agent 3 (Personalization), and Frontend.
    """
    evaluation_id: str = Field(default_factory=lambda: f"eval_{uuid.uuid4().hex[:8]}")
    question_id: str

    # Answer Correctness vs Concept Understanding
    correctness: float = Field(..., ge=0.0, le=1.0, description="Graded answer correctness (0.0 to 1.0)")
    classification: EvaluationClassification
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Confidence in the evaluation itself")

    concept: str
    concept_understanding: float = Field(
        ..., ge=0.0, le=1.0,
        description="Estimate of true underlying conceptual understanding, separated from raw answer"
    )

    # Reasoning quality (0.0 to 1.0, null for MCQs where no reasoning was provided)
    reasoning_quality: Optional[float] = Field(
        default=None, ge=0.0, le=1.0,
        description="Logical consistency, validity of intermediate steps, null for pure MCQ"
    )

    # Diagnosis: Misconception vs Knowledge Gap
    misconception: MisconceptionDetails = Field(default_factory=MisconceptionDetails)
    knowledge_gap: List[str] = Field(default_factory=list)

    # Pedagogical Adaptation Recommendation
    recommended_action: str = "CONTINUE"
    recommended_strategy: Optional[str] = None  # analogy, visual, worked_example, simplification, formula, etc.
    difficulty_adjustment: Literal["decrease", "maintain", "increase"] = "maintain"
    difficulty_delta: float = Field(default=0.0, ge=-0.5, le=0.5)

    # Follow-up Recommendation
    follow_up_required: bool = False
    follow_up_focus: Optional[str] = None

    # Transparent pedagogical evidence (short bullet points, no hidden chain-of-thought)
    evidence: List[str] = Field(default_factory=list)

    # Status
    evaluation_status: EvaluationStatus = "success"

    # Optional backwards-compatibility fields for legacy callers
    teacher_thought: Optional[str] = None
    bloom_level: Optional[str] = None
