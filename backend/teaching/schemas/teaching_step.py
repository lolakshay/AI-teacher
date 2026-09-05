"""
TeachingStep Data Contract conforming to Section 5.4.
This is the primary output contract consumed by Frontend, TTS, Video, and Avatar subsystems.
"""

from typing import List, Optional, Literal, Any, Dict
from pydantic import BaseModel, Field
import uuid

StepType = Literal[
    "introduction",
    "explanation",
    "example",
    "demonstration",
    "visual",
    "question",
    "re_explanation",
    "summary",
    "assessment_trigger",
    "lesson_complete"
]

VisualType = Literal[
    "diagram",
    "equation",
    "graph",
    "code",
    "timeline",
    "map",
    "process",
    "image",
    "none"
]

class VisualInstructionPayload(BaseModel):
    required: bool = False
    visual_type: VisualType = "none"
    description: str = ""
    data: Optional[Dict[str, Any]] = None  # Supplemental visual payload if available

class QuestionPayload(BaseModel):
    enabled: bool = False
    question_id: Optional[str] = None
    question_type: Optional[str] = None  # "conceptual", "mcq", "short_answer", "application", "diagnostic", "follow_up"
    question_text: Optional[str] = None
    expected_concept: Optional[str] = None
    options: Optional[List[str]] = None
    hints: List[str] = Field(default_factory=list)

class TeachingStep(BaseModel):
    step_id: str = Field(default_factory=lambda: f"step_{uuid.uuid4().hex[:8]}")
    session_id: str
    lesson_id: str
    concept_id: Optional[str] = None
    step_index: int = 0
    step_type: StepType = "explanation"

    teaching_objective: str = ""
    content: str = ""
    spoken_script: str = ""
    language: str = "English"
    difficulty: float = Field(default=0.5, ge=0.0, le=1.0)

    visual_instruction: VisualInstructionPayload = Field(
        default_factory=VisualInstructionPayload
    )
    question: QuestionPayload = Field(default_factory=QuestionPayload)
    source_references: List[Any] = Field(default_factory=list)

    await_student_response: bool = False
    next_action_hint: str = "continue"
    avatar_emotion: str = "explaining"  # explaining, encouraging, thoughtful, celebrating, attentive
