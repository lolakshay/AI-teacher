"""
Adaptation package.
"""

from backend.evaluation.adaptation.rules import (
    CORRECTNESS_STRONG_THRESHOLD,
    CORRECTNESS_MODERATE_THRESHOLD,
    CORRECTNESS_PARTIAL_THRESHOLD,
    STRATEGY_PROGRESSION,
    get_next_strategy,
)
from backend.evaluation.adaptation.engine import (
    AdaptationEngine,
    adaptation_engine,
)

__all__ = [
    "CORRECTNESS_STRONG_THRESHOLD",
    "CORRECTNESS_MODERATE_THRESHOLD",
    "CORRECTNESS_PARTIAL_THRESHOLD",
    "STRATEGY_PROGRESSION",
    "get_next_strategy",
    "AdaptationEngine",
    "adaptation_engine",
]
