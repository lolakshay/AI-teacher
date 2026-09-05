"""
LessonPlan Data Contract conforming to Section 5.3.
"""

from typing import List, Dict, Any, Literal
from pydantic import BaseModel, Field
import uuid
from backend.teaching.schemas.concept_node import ConceptNode

QuestionFrequency = Literal["low", "medium", "high"]

class QuestionStrategy(BaseModel):
    frequency: QuestionFrequency = "medium"
    checkpoint_after_concepts: int = 1
    question_types: List[str] = Field(
        default_factory=lambda: ["conceptual", "mcq", "short_answer", "application"]
    )

class AssessmentStrategy(BaseModel):
    enabled: bool = True
    estimated_questions: int = 3

class LessonPlan(BaseModel):
    lesson_id: str = Field(default_factory=lambda: f"les_{uuid.uuid4().hex[:8]}")
    title: str
    topic: str
    learner_level: str = "beginner"
    language: str = "English"
    available_minutes: float = 20.0
    objectives: List[str] = Field(default_factory=list)
    prerequisites: List[str] = Field(default_factory=list)
    concepts: List[ConceptNode] = Field(default_factory=list)
    ordered_concept_ids: List[str] = Field(default_factory=list)
    estimated_duration_minutes: float = 20.0
    teaching_strategy: str = "Direct explanation with intuitive analogies, dynamic visuals, and interactive checks"
    question_strategy: QuestionStrategy = Field(default_factory=QuestionStrategy)
    assessment_strategy: AssessmentStrategy = Field(default_factory=AssessmentStrategy)
