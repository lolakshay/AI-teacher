"""
Base Evaluator Interface for Agent 6.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from backend.evaluation.schemas import StudentResponse, QuestionContext, EvaluationResult


class BaseResponseEvaluator(ABC):
    """
    Abstract interface for evaluating student responses.
    """

    @abstractmethod
    def can_evaluate(self, response: StudentResponse, context: QuestionContext) -> bool:
        """Determines if this evaluator can handle the given response & question."""
        pass

    @abstractmethod
    def evaluate(
        self,
        response: StudentResponse,
        context: QuestionContext,
        learner_context: Optional[Dict[str, Any]] = None
    ) -> EvaluationResult:
        """Performs evaluation and returns structured EvaluationResult."""
        pass
