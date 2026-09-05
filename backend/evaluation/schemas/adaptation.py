"""
Adaptation Decision and Follow-up Schemas for Agent 6.
Conforms to Sections 14, 15, 16, 17, 18, 19, 20, 21, and 38.
"""

from typing import Optional, Literal
from pydantic import BaseModel, Field

AdaptationAction = Literal[
    "CONTINUE",
    "CLARIFY",
    "RE_EXPLAIN",
    "USE_ANALOGY",
    "SHOW_WORKED_EXAMPLE",
    "SIMPLIFY",
    "REVIEW_PREREQUISITE",
    "ASK_FOLLOWUP",
    "DECREASE_DIFFICULTY",
    "INCREASE_DIFFICULTY",
    "RETRY_CONCEPT",
    "MOVE_TO_NEXT_CONCEPT",
]

ExplanationStrategy = Literal[
    "analogy",
    "visual",
    "worked_example",
    "step_by_step",
    "simplification",
    "formula_derivation",
    "physical_intuition",
    "counter_example",
]


class FollowUpRecommendation(BaseModel):
    """
    Specification for a follow-up diagnostic probe question.
    Agent 1 uses this to formulate the next probe without Agent 6 becoming a full planner.
    """
    required: bool = False
    concept: str = ""
    difficulty: float = Field(default=0.3, ge=0.0, le=1.0)
    question_type: str = "conceptual"
    focus: str = ""
    reason: str = ""


class AdaptationDecision(BaseModel):
    """
    The actionable adaptation recommendation consumed directly by Agent 1 (Teaching Orchestrator).
    """
    action: AdaptationAction = "CONTINUE"
    focus_concept: str = ""
    strategy: Optional[ExplanationStrategy] = None
    difficulty_adjustment: Literal["decrease", "maintain", "increase"] = "maintain"
    difficulty_delta: float = Field(default=0.0, ge=-0.5, le=0.5)
    target_difficulty: Optional[float] = None
    question_after_reteach: bool = False
    follow_up: FollowUpRecommendation = Field(default_factory=FollowUpRecommendation)
    reason: str = ""
    prerequisite_to_review: Optional[str] = None
