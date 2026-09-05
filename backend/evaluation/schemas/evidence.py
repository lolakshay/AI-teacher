"""
Learning Evidence Schema for Agent 3 (Personalization Engine).
Conforms to Sections 22, 23, 41, and 46.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime, timezone


class LearningEvidence(BaseModel):
    """
    Standard evidence packet sent to Agent 3 (Personalization / Learner Modeling).
    Agent 3 uses this to update mastery, record misconceptions, and track learning curves.
    """
    student_id: str
    session_id: str
    question_id: str
    concept: str
    correctness: float = Field(..., ge=0.0, le=1.0)
    concept_understanding: float = Field(..., ge=0.0, le=1.0)
    classification: str = "evaluated"
    misconception_detected: bool = False
    misconception_type: Optional[str] = None
    misconception_description: Optional[str] = None
    knowledge_gap: List[str] = Field(default_factory=list)
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    reasoning_quality: Optional[float] = None
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    details: Dict[str, Any] = Field(default_factory=dict)

    def to_agent3_payload(self) -> Dict[str, Any]:
        """
        Formats directly into the payload accepted by
        backend.personalization.service.PersonalizationService.update_concept_knowledge
        """
        return {
            "source": "lesson_response",
            "session_id": self.session_id,
            "question_id": self.question_id,
            "correctness": self.correctness,
            "classification": self.classification,
            "misconception": self.misconception_description if self.misconception_detected else None,
            "confidence": self.confidence,
            "details": {
                "concept_understanding": self.concept_understanding,
                "misconception_type": self.misconception_type,
                "knowledge_gap": self.knowledge_gap,
                "reasoning_quality": self.reasoning_quality,
                **self.details
            }
        }
