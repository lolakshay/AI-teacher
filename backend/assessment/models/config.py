"""
Assessment Configuration Data Contract conforming to Section 6.
Defines parameters for creating and orchestrating an assessment.
"""

from typing import List, Dict, Any, Optional, Literal
from pydantic import BaseModel, Field
import uuid

QuestionType = Literal[
    "mcq",
    "short_answer",
    "numerical",
    "conceptual",
    "problem_solving",
    "application",
    "explain_in_own_words"
]


class AssessmentConfig(BaseModel):
    assessment_id: str = Field(default_factory=lambda: f"assess_{uuid.uuid4().hex[:8]}")
    lesson_id: Optional[str] = None
    student_id: Optional[str] = None
    topic: str
    question_count: int = Field(default=5, ge=1, le=50)
    duration_minutes: Optional[int] = Field(default=None, ge=1)
    question_types: List[QuestionType] = Field(
        default_factory=lambda: ["mcq", "short_answer", "numerical", "conceptual"]
    )
    difficulty: float = Field(default=0.4, ge=0.0, le=1.0)
    coverage: List[str] = Field(default_factory=list)  # Target concepts to assess
    passing_score: float = Field(default=0.70, ge=0.0, le=1.0)

    # Optional configuration fields
    difficulty_distribution: Optional[Dict[str, float]] = Field(
        default_factory=lambda: {"easy": 0.3, "medium": 0.5, "hard": 0.2}
    )
    randomize: bool = False
    random_seed: Optional[int] = None
    attempt_limit: Optional[int] = 1
    language: str = "English"  # English, Hindi, Hinglish
    source_references: List[Dict[str, Any]] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
