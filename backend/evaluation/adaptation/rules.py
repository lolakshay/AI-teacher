"""
Adaptation Rules and Strategy Progressions for Agent 6.
Conforms to Sections 7, 14, 15, 16, 19, 20, 21.
"""

from typing import List
from backend.evaluation.schemas.adaptation import ExplanationStrategy

# Score thresholds
CORRECTNESS_STRONG_THRESHOLD = 0.85
CORRECTNESS_MODERATE_THRESHOLD = 0.60
CORRECTNESS_PARTIAL_THRESHOLD = 0.30

# Strategy cycle: When a strategy fails, select the next distinct strategy
STRATEGY_PROGRESSION: List[ExplanationStrategy] = [
    "analogy",
    "visual",
    "worked_example",
    "step_by_step",
    "simplification",
    "physical_intuition",
    "counter_example",
    "formula_derivation"
]


def get_next_strategy(previous_strategies: List[str]) -> ExplanationStrategy:
    """
    Returns a novel explanation strategy that has not been recently failed.
    Prevents the teacher from repeating the same explanation style.
    """
    used = set(s.lower() for s in previous_strategies if s)
    for strat in STRATEGY_PROGRESSION:
        if strat not in used:
            return strat
    # If all used, default to concrete physical intuition or worked example
    return "physical_intuition"
