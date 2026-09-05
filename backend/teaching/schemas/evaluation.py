"""
Evaluation Data Contract conforming to Section 18.
"""

from typing import Optional, Literal
from pydantic import BaseModel, Field
from datetime import datetime, timezone

EvaluationClassification = Literal[
    "correct",
    "partially_correct",
    "incorrect",
    "misconception",
    "unclear"
]

class StudentResponse(BaseModel):
    session_id: str
    question_id: str
    student_answer: str
    answer_type: str = "text"
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class EvaluationResult(BaseModel):
    correctness: float = Field(..., ge=0.0, le=1.0)
    classification: EvaluationClassification
    misconception: Optional[str] = None
    knowledge_gap: Optional[str] = None
    recommended_action: str = "continue"
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    reasoning_quality: str = "Satisfactory"
    teacher_thought: str = ""
    concept: str = ""
