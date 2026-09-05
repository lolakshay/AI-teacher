"""
Session State Data Contract conforming to Section 6.
"""

from typing import List, Dict, Optional, Literal, Any
from pydantic import BaseModel, Field
import uuid
from backend.teaching.schemas.lesson_plan import LessonPlan
from backend.teaching.schemas.teaching_step import TeachingStep

SessionStatus = Literal[
    "planning",
    "teaching",
    "waiting_for_response",
    "adapting",
    "assessment",
    "completed",
    "failed"
]

ConceptStatus = Literal[
    "not_started",
    "teaching",
    "partially_understood",
    "understood",
    "struggling"
]

class ConceptProgress(BaseModel):
    status: ConceptStatus = "not_started"
    attempts: int = 0
    last_score: Optional[float] = None
    strategies_used: List[str] = Field(default_factory=list)

class TeachingSessionState(BaseModel):
    session_id: str = Field(default_factory=lambda: f"ses_{uuid.uuid4().hex[:8]}")
    student_id: str
    lesson_id: str
    status: SessionStatus = "planning"

    current_concept_id: Optional[str] = None
    current_step_index: int = 0

    concept_progress: Dict[str, ConceptProgress] = Field(default_factory=dict)
    completed_concepts: List[str] = Field(default_factory=list)
    struggling_concepts: List[str] = Field(default_factory=list)

    questions_asked: int = 0
    questions_correct: int = 0
    adaptation_count: int = 0
    remaining_time_minutes: float = 20.0
    preferred_language: str = "English"

    history: List[Dict[str, Any]] = Field(default_factory=list)
    lesson_plan: Optional[LessonPlan] = None
    steps: List[TeachingStep] = Field(default_factory=list)

    active_question: Optional[Dict[str, Any]] = None
    active_misconception: Optional[str] = None
    is_paused: bool = False
