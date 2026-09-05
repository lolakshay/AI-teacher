"""
Assessment Question Data Contract conforming to Section 7 & Section 32.
Represents individual assessment questions across diverse question types.
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


class AssessmentQuestion(BaseModel):
    question_id: str = Field(default_factory=lambda: f"q_{uuid.uuid4().hex[:8]}")
    assessment_id: str
    text: str  # The prompt or problem statement
    type: QuestionType = "conceptual"
    
    # MCQ specific
    options: Optional[List[str]] = None
    correct_option: Optional[str] = None  # e.g., "B" or the exact option text
    
    # Short answer / Conceptual specific
    expected_answer: Optional[str] = None
    
    # Numerical specific
    expected_value: Optional[float] = None
    unit: Optional[str] = None
    tolerance: Optional[float] = 0.05  # 5% relative tolerance or absolute default
    
    # Pedagogical tagging
    expected_concept: str
    difficulty: float = Field(default=0.4, ge=0.0, le=1.0)
    points: float = Field(default=1.0, gt=0.0)
    rubric: List[str] = Field(default_factory=list)
    
    # RAG grounding traceability (Section 11)
    source_references: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Optional metadata (e.g. bloom_level, hints, tags)
    metadata: Dict[str, Any] = Field(default_factory=dict)
