"""
Question Context Schema for Agent 6.
Conforms to Sections 5, 27, 28, 31, and 32.
"""

from typing import List, Dict, Any, Optional, Literal, Union
from pydantic import BaseModel, Field


class RubricItem(BaseModel):
    criterion: str
    weight: float = 1.0
    description: str = ""


class MisconceptionDefinition(BaseModel):
    type: str
    trigger_patterns: List[str] = Field(default_factory=list)
    description: str = ""


class NumericalToleranceConfig(BaseModel):
    tolerance_type: Literal["absolute", "relative", "percentage"] = "relative"
    tolerance_value: float = 0.05  # Default 5% relative tolerance
    expected_unit: Optional[str] = None
    require_unit: bool = False


class QuestionContext(BaseModel):
    """
    Rich context provided by upstream agents (e.g. Agent 1 / Lesson Planner).
    All fields are optional with safe defaults if upstream agent provides minimal data.
    """
    question_id: str
    question_text: str
    question_type: str = "conceptual"  # mcq, short_answer, conceptual, numerical, explain_in_own_words
    expected_answer: str = ""
    expected_concept: str = ""
    related_concepts: List[str] = Field(default_factory=list)
    difficulty: float = Field(default=0.5, ge=0.0, le=1.0)
    learning_objective: str = ""
    rubric: List[Union[RubricItem, str]] = Field(default_factory=list)
    source_references: List[Dict[str, Any]] = Field(default_factory=list)

    # Rich pedagogical hints
    expected_reasoning: Optional[str] = None
    acceptable_alternate_answers: List[str] = Field(default_factory=list)
    common_misconceptions: List[MisconceptionDefinition] = Field(default_factory=list)
    prerequisite_concepts: List[str] = Field(default_factory=list)

    # Specialized question data
    options: Optional[List[str]] = None  # e.g. ["A) Current decreases", "B) Current increases"]
    correct_option: Optional[str] = None  # e.g. "A" or "Current decreases"
    numerical_config: Optional[NumericalToleranceConfig] = None
