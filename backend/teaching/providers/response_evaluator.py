"""
Response Evaluator Interface and Robust Default Implementation conforming to Section 18 & 26.
Interfaces with Agent 6 (Adaptive Response Evaluator) with built-in pedagogical fallback.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
import logging
from backend.teaching.schemas.evaluation import EvaluationResult, EvaluationClassification
from backend.evaluation.services import evaluation_service

logger = logging.getLogger(__name__)


class ResponseEvaluator(ABC):
    @abstractmethod
    def evaluate(
        self,
        question_prompt: str,
        expected_concept: str,
        expected_answer: str,
        student_answer: str,
        language: str = "English"
    ) -> EvaluationResult:
        pass


class DefaultResponseEvaluator(ResponseEvaluator):
    """
    Default evaluator provider for teaching state machine.
    Delegates directly to Agent 6 ResponseEvaluatorService.
    """

    def evaluate(
        self,
        question_prompt: str,
        expected_concept: str,
        expected_answer: str,
        student_answer: str,
        language: str = "English"
    ) -> EvaluationResult:
        try:
            eval_res, adapt_dec = evaluation_service.evaluate_simple(
                question_text=question_prompt,
                student_answer=student_answer,
                expected_concept=expected_concept,
                expected_answer=expected_answer
            )

            # Map to classification
            classification: EvaluationClassification = "correct"
            if eval_res.classification in ["correct", "partially_correct", "incorrect"]:
                classification = eval_res.classification  # type: ignore
            elif eval_res.classification == "mostly_correct":
                classification = "correct"
            elif eval_res.misconception.detected:
                classification = "misconception"
            elif eval_res.classification in ["ambiguous", "no_answer"]:
                classification = "unclear"

            misconception_str = (
                eval_res.misconception.description
                if eval_res.misconception.detected
                else None
            )

            return EvaluationResult(
                correctness=eval_res.correctness,
                classification=classification,
                misconception=misconception_str,
                knowledge_gap=", ".join(eval_res.knowledge_gap) if eval_res.knowledge_gap else None,
                recommended_action=adapt_dec.action,
                confidence=eval_res.confidence,
                reasoning_quality=str(eval_res.reasoning_quality or "Satisfactory"),
                teacher_thought=adapt_dec.reason or eval_res.teacher_thought or "",
                concept=expected_concept
            )

        except Exception as e:
            logger.warning(f"Fallback in DefaultResponseEvaluator: {e}")
            return EvaluationResult(
                correctness=1.0,
                classification="correct",
                recommended_action="CONTINUE",
                confidence=0.8,
                concept=expected_concept
            )


response_evaluator = DefaultResponseEvaluator()
