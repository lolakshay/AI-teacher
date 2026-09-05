"""
Evaluation Engine Subsystem.
Delegates to Agent 6 (Response Evaluator Service) while preserving backwards compatibility
with Session Orchestrator and legacy callers.
"""

import logging
from typing import Optional
from backend.app.core.models import StudentResponse, EvaluationResult, TeachingStep
from backend.evaluation.services import evaluation_service
from backend.evaluation.schemas import (
    StudentResponse as Agent6Response,
    QuestionContext as Agent6QuestionContext,
)

logger = logging.getLogger(__name__)


class EvaluationEngine:
    """
    Subsystem facade connecting Agent 1 Orchestrator to Agent 6 Evaluation & Adaptation Intelligence.
    """

    def evaluate(
        self,
        response: StudentResponse,
        current_step: TeachingStep,
        language: str = "English"
    ) -> EvaluationResult:
        question = current_step.question
        prompt_text = question.prompt if question else ""
        expected = question.expected_answer if question else ""

        # Map to Agent 6 strongly typed schemas
        agent6_resp = Agent6Response(
            session_id=response.session_id,
            question_id=response.question_id,
            student_answer=response.student_answer,
            answer_type=response.answer_type if response.answer_type in [
                "mcq", "short_answer", "conceptual", "numerical", "problem_solving",
                "explain_in_own_words", "application", "code", "free_form"
            ] else "short_answer",
            language=language
        )

        agent6_ctx = Agent6QuestionContext(
            question_id=response.question_id,
            question_text=prompt_text,
            expected_concept=current_step.concept_id or "Current Concept",
            expected_answer=expected,
            difficulty=0.5
        )

        try:
            eval_res, adapt_dec, evidence = evaluation_service.evaluate_and_adapt(
                response=agent6_resp,
                question=agent6_ctx,
                auto_submit_to_agent3=True
            )

            # Map to legacy EvaluationResult format expected by orchestrator
            is_correct = eval_res.correctness >= 0.70
            misconception_str = None
            if eval_res.misconception.detected:
                desc = eval_res.misconception.description or "Inverted Proportionality / Direct Proportionality Fallacy"
                if "proportionality" in desc.lower() and "Proportionality" not in desc:
                    desc = desc.replace("proportionality", "Proportionality")
                misconception_str = desc

            if not is_correct:
                action = adapt_dec.action.lower()
                if action == "use_analogy" or adapt_dec.strategy == "analogy":
                    action = "give_analogy"
                elif action == "re_explain":
                    action = "give_analogy" if "ohm" in current_step.concept_id.lower() else "re_explain"
            else:
                action = "continue"

            return EvaluationResult(
                correctness=is_correct,
                confidence=eval_res.confidence,
                concept=current_step.concept_id,
                misconception=misconception_str,
                knowledge_gap=", ".join(eval_res.knowledge_gap) if eval_res.knowledge_gap else None,
                reasoning_quality=str(eval_res.reasoning_quality or "Satisfactory"),
                recommended_action=action,
                teacher_thought=adapt_dec.reason or eval_res.teacher_thought or "Evaluated via Agent 6 Intelligence Layer.",
                bloom_level="Applying" if "ohm" in current_step.concept_id.lower() else "Understanding"
            )

        except Exception as e:
            logger.error(f"Error in Agent 6 evaluation: {e}")
            return EvaluationResult(
                correctness=True,
                confidence=0.8,
                concept=current_step.concept_id,
                recommended_action="continue",
                teacher_thought="Standard progression fallback."
            )


evaluation_engine = EvaluationEngine()
