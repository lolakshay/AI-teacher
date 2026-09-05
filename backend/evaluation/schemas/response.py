"""
Student Response Schema for Agent 6.
Conforms to Sections 4, 30, and 34 of the Specification.
"""

from typing import Literal, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime, timezone

AnswerType = Literal[
    "mcq",
    "short_answer",
    "conceptual",
    "numerical",
    "problem_solving",
    "explain_in_own_words",
    "application",
    "code",
    "free_form",
]


class StudentResponse(BaseModel):
    """
    Standard incoming student response representation.
    Treats student_answer as untrusted user input.
    """
    session_id: str
    question_id: str
    student_answer: str = Field(..., max_length=5000, description="Untrusted student answer text")
    answer_type: AnswerType = "short_answer"
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    language: str = "en"
    metadata: Dict[str, Any] = Field(default_factory=dict)
