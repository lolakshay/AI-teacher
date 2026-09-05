"""
Assessment Result & Analytics Data Contracts conforming to Section 15, 17, 45, 46, 47.
Provides fine-grained, concept-level and multi-dimensional evaluation results.
"""

from typing import List, Dict, Any, Optional, Literal
from pydantic import BaseModel, Field
from datetime import datetime, timezone

ConceptStatus = Literal["unknown", "weak", "developing", "strong"]
ResultClassification = Literal[
    "correct",
    "partially_correct",
    "incorrect",
    "misconception",
    "unclear",
    "skipped"
]


class ScoreSummary(BaseModel):
    raw: float
    max: float
    percentage: float = Field(..., ge=0.0, le=1.0)
    passed: bool = False


class QuestionResult(BaseModel):
    question_id: str
    concept: str
    correctness: float = Field(..., ge=0.0, le=1.0)
    points_earned: float
    points_possible: float
    classification: ResultClassification
    misconception: Optional[str] = None
    knowledge_gap: Optional[str] = None
    evaluation_confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    reasoning_quality: str = "Satisfactory"
    feedback: str = ""
    is_skipped: bool = False


class ConceptResult(BaseModel):
    concept: str
    score: float = Field(..., ge=0.0, le=1.0)
    questions_attempted: int = 0
    questions_correct: int = 0
    status: ConceptStatus = "unknown"
    revision_required: bool = False
    misconceptions: List[str] = Field(default_factory=list)


class AggregatedMisconception(BaseModel):
    misconception: str
    concept: str
    frequency: int = 1
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    description: str = ""


class WeakAreaItem(BaseModel):
    concept: str
    score: float
    reason: str
    misconceptions: List[str] = Field(default_factory=list)


class AssessmentResult(BaseModel):
    assessment_id: str
    session_id: Optional[str] = None
    student_id: str
    lesson_id: Optional[str] = None
    topic: str
    score: ScoreSummary
    question_results: List[QuestionResult] = Field(default_factory=list)
    concept_results: List[ConceptResult] = Field(default_factory=list)
    weak_areas: List[WeakAreaItem] = Field(default_factory=list)
    strong_areas: List[str] = Field(default_factory=list)
    misconceptions: List[AggregatedMisconception] = Field(default_factory=list)
    difficulty_breakdown: Dict[str, Dict[str, float]] = Field(default_factory=dict)
    question_type_breakdown: Dict[str, Dict[str, float]] = Field(default_factory=dict)
    status: str = "completed"
    completed_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
