"""
Agent 6 Evaluator Bridge conforming to Section 27 & Section 61.
Delegates individual answer evaluation to Agent 6 (Response Evaluator)
without duplicating open-ended evaluator logic.
"""

import logging
from typing import Optional, Dict, Any
from backend.assessment.models.question import AssessmentQuestion
from backend.assessment.models.session import AssessmentResponse
from backend.teaching.schemas.evaluation import EvaluationResult, StudentResponse as Agent6StudentResponse
from backend.app.core.models import TeachingStep, QuestionPayload

logger = logging.getLogger(__name__)


class EvaluatorBridge:
    """
    Subsystem interface connecting Agent 7 to Agent 6.
    Ensures Agent 7 consumes Agent 6's evaluation rather than reinventing it.
    """

    def __init__(self, evaluator=None):
        self._evaluator = evaluator

    def get_evaluator(self):
        if self._evaluator is not None:
            return self._evaluator
        try:
            from backend.app.services.evaluation_engine import evaluation_engine
            return evaluation_engine
        except Exception as e:
            logger.warning(f"Could not load evaluation_engine: {e}")
            return None

    def evaluate_response(
        self,
        question: AssessmentQuestion,
        response: AssessmentResponse,
        language: str = "English"
    ) -> Dict[str, Any]:
        """
        Sends question context and student response to Agent 6.
        Returns normalized evaluation dictionary:
        {
            "correctness": float (0.0 - 1.0),
            "classification": str,
            "misconception": Optional[str],
            "knowledge_gap": Optional[str],
            "confidence": float,
            "reasoning_quality": str,
            "teacher_thought": str
        }
        """
        evaluator = self.get_evaluator()
        if evaluator is None:
            # Fallback if Agent 6 unavailable
            return {
                "correctness": 0.5,
                "classification": "unclear",
                "misconception": None,
                "knowledge_gap": "Evaluator unavailable",
                "confidence": 0.0,
                "reasoning_quality": "Evaluation service unavailable",
                "teacher_thought": "Agent 6 evaluator was not reachable."
            }

        # Build teaching step mock representation to adapt to Agent 6's interface
        q_payload = QuestionPayload(
            question_id=question.question_id,
            prompt=question.text,
            expected_answer=question.expected_answer or "",
            options=question.options,
            hints=[]
        )
        step = TeachingStep(
            step_id=f"step_{question.question_id}",
            lesson_id=question.assessment_id,
            concept_id=question.expected_concept,
            step_type="assessment",
            objective=f"Assess concept {question.expected_concept}",
            explanation="",
            question=q_payload
        )

        std_response = Agent6StudentResponse(
            session_id=question.assessment_id,
            question_id=question.question_id,
            student_answer=response.answer,
            answer_type="text"
        )

        try:
            # Call Agent 6
            eval_res = evaluator.evaluate(
                response=std_response,
                current_step=step,
                language=language
            )

            # Extract normalized fields
            if hasattr(eval_res, "correctness"):
                raw_corr = eval_res.correctness
                # Agent 6 may return bool or float
                corr_float = 1.0 if raw_corr is True else (0.0 if raw_corr is False else float(raw_corr))
            else:
                corr_float = 0.5

            classification = getattr(eval_res, "classification", None)
            if not classification:
                if getattr(eval_res, "misconception", None):
                    classification = "misconception"
                elif corr_float >= 0.8:
                    classification = "correct"
                elif corr_float >= 0.4:
                    classification = "partially_correct"
                else:
                    classification = "incorrect"

            return {
                "correctness": corr_float,
                "classification": str(classification),
                "misconception": getattr(eval_res, "misconception", None),
                "knowledge_gap": getattr(eval_res, "knowledge_gap", None),
                "confidence": float(getattr(eval_res, "confidence", 1.0)),
                "reasoning_quality": str(getattr(eval_res, "reasoning_quality", "Satisfactory")),
                "teacher_thought": str(getattr(eval_res, "teacher_thought", ""))
            }
        except Exception as e:
            logger.error(f"Error invoking Agent 6 evaluate: {e}")
            return {
                "correctness": 0.0,
                "classification": "incorrect",
                "misconception": None,
                "knowledge_gap": f"Evaluation error: {str(e)}",
                "confidence": 0.0,
                "reasoning_quality": "Evaluation failed",
                "teacher_thought": "Failed to process through Agent 6."
            }


evaluator_bridge = EvaluatorBridge()
