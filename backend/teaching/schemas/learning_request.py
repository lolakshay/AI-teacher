"""
LearningRequest Data Contract conforming to Section 5.1.
At least ONE must exist: topic OR material_id.
"""

from typing import List, Optional, Literal
from pydantic import BaseModel, Field, model_validator
import uuid

EducationalLevel = Literal["beginner", "intermediate", "advanced", "custom"]
TeachingStyle = Literal[
    "simple",
    "analogy_based",
    "conceptual",
    "practical",
    "exam_focused",
    "technical",
    "custom"
]
DesiredDepth = Literal["quick", "standard", "deep", "exhaustive"]

class LearningRequest(BaseModel):
    request_id: str = Field(default_factory=lambda: f"req_{uuid.uuid4().hex[:8]}")
    student_id: str = Field(default_factory=lambda: f"stu_{uuid.uuid4().hex[:8]}")
    topic: Optional[str] = None
    material_id: Optional[str] = None

    educational_level: EducationalLevel = "beginner"
    existing_knowledge: List[str] = Field(default_factory=list)
    learning_objective: str = "Understand foundational principles and apply them effectively"

    preferred_language: str = "English"
    teaching_style: TeachingStyle = "analogy_based"

    available_time_minutes: float = 20.0
    desired_depth: DesiredDepth = "standard"

    @model_validator(mode="after")
    def validate_topic_or_material(self) -> "LearningRequest":
        has_topic = bool(self.topic and self.topic.strip())
        has_material = bool(self.material_id and self.material_id.strip())
        if not has_topic and not has_material:
            raise ValueError("At least ONE must exist: 'topic' OR 'material_id'.")
        return self
