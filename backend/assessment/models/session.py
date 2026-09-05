"""
Assessment Session & Response Data Contracts conforming to Section 13 & Section 14.
Manages student attempts, progress tracking, response capture, and timeouts.
"""

from typing import List, Dict, Any, Optional, Literal
from pydantic import BaseModel, Field
from datetime import datetime, timezone
import uuid

SessionStatus = Literal[
    "created",
    "in_progress",
    "paused",
    "submitted",
    "evaluating",
    "completed",
    "failed",
    "timed_out"
]


class AssessmentResponse(BaseModel):
    question_id: str
    student_id: str
    answer: str
    submitted_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    language: str = "en"
    is_skipped: bool = False
    time_spent_seconds: Optional[float] = None


class AssessmentSession(BaseModel):
    session_id: str = Field(default_factory=lambda: f"asess_{uuid.uuid4().hex[:8]}")
    assessment_id: str
    student_id: str
    started_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    completed_at: Optional[str] = None
    current_question_index: int = 0
    responses: List[AssessmentResponse] = Field(default_factory=list)
    status: SessionStatus = "created"
    duration_minutes: Optional[int] = None
    time_remaining_seconds: Optional[float] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
