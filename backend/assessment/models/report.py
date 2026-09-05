"""
Learning Report Data Contract conforming to Section 24 & Section 40-42.
The final educational outcome delivered to Agent 1, Agent 3, and the student.
"""

from typing import List, Dict, Any, Optional, Literal
from pydantic import BaseModel, Field
from datetime import datetime, timezone
import uuid
from backend.assessment.models.result import ScoreSummary

RevisionPriority = Literal["high", "medium", "low"]


class RevisionRecommendation(BaseModel):
    concept: str
    priority: RevisionPriority = "medium"
    reason: str
    recommended_activity: str
    estimated_time_minutes: int = 10


class LearningReport(BaseModel):
    report_id: str = Field(default_factory=lambda: f"rep_{uuid.uuid4().hex[:8]}")
    student_id: str
    lesson_id: Optional[str] = None
    assessment_id: str
    topic: str
    score: ScoreSummary
    concepts_understood: List[str] = Field(default_factory=list)
    strong_areas: List[str] = Field(default_factory=list)
    weak_areas: List[str] = Field(default_factory=list)
    misconceptions: List[str] = Field(default_factory=list)
    concepts_requiring_revision: List[str] = Field(default_factory=list)
    recommended_revision: List[RevisionRecommendation] = Field(default_factory=list)
    recommended_next_topic: Optional[str] = None  # None if no learning path context exists (No-Evidence Rule)
    next_topic_reasoning: Optional[str] = None
    overall_progress: float = Field(..., ge=0.0, le=1.0)
    human_readable_summary: str = ""
    completed_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
