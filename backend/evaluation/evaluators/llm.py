"""
LLM-Powered Response Evaluator for Agent 6.
Conforms to Sections 24, 25, 26, 33, 34, 53, 54, 55, 56.
"""

import json
import logging
from typing import Optional, Dict, Any
from backend.evaluation.evaluators.base import BaseResponseEvaluator
from backend.evaluation.schemas import (
    StudentResponse,
    QuestionContext,
    EvaluationResult,
    MisconceptionDetails,
)
from backend.evaluation.prompts import (
    SYSTEM_EVALUATION_INSTRUCTION,
    EVALUATION_USER_PROMPT_TEMPLATE,
)
from backend.evaluation.normalizers import text_normalizer
from backend.evaluation.evaluators.deterministic import deterministic_evaluator
from backend.app.services.llm_service import llm_service

logger = logging.getLogger(__name__)


class LLMResponseEvaluator(BaseResponseEvaluator):
    """
    LLM-powered evaluator for open-ended, conceptual, and explain-in-own-words responses.
    Includes strict prompt injection defenses, JSON structure guarantees, and deterministic fallback.
    """

    def can_evaluate(self, response: StudentResponse, context: QuestionContext) -> bool:
        # LLM evaluator can handle any text question as fallback or primary
        return True

    def evaluate(
        self,
        response: StudentResponse,
        context: QuestionContext,
        learner_context: Optional[Dict[str, Any]] = None
    ) -> EvaluationResult:
        raw_answer = (response.student_answer or "").strip()

        # 1. Sanitize untrusted input (Section 26 & 56)
        sanitized_answer = text_normalizer.sanitize_untrusted_input(raw_answer, max_chars=3000)

        # 2. Format rubric and learner context string
        rubric_str = json.dumps(
            [r.dict() if hasattr(r, "dict") else r for r in context.rubric]
            if context.rubric else ["Pedagogical accuracy of concept explanation"]
        )
        learner_str = json.dumps(learner_context or {})

        user_prompt = EVALUATION_USER_PROMPT_TEMPLATE.format(
            question_text=context.question_text,
            expected_concept=context.expected_concept,
            expected_answer=context.expected_answer,
            rubric=rubric_str,
            learner_context=learner_str,
            student_answer=sanitized_answer
        )

        # Fallback template if LLM is offline or fails
        fallback_data = {
            "correctness": 0.5,
            "classification": "partially_correct",
            "confidence": 0.7,
            "concept_understanding": 0.5,
            "reasoning_quality": 0.5,
            "misconception": {
                "detected": False,
                "type": None,
                "description": None,
                "confidence": 0.0
            },
            "knowledge_gap": [context.expected_concept],
            "recommended_action": "CLARIFY",
            "recommended_strategy": "step_by_step",
            "difficulty_adjustment": "maintain",
            "difficulty_delta": 0.0,
            "follow_up_required": True,
            "follow_up_focus": context.expected_concept,
            "evidence": ["Evaluated with deterministic pedagogical fallback."]
        }

        try:
            res_json = llm_service.generate_json(
                prompt=user_prompt,
                system_instruction=SYSTEM_EVALUATION_INSTRUCTION,
                fallback_data=fallback_data
            )

            if not res_json or not isinstance(res_json, dict):
                logger.warning("LLM returned non-dict response; applying deterministic fallback.")
                return deterministic_evaluator.evaluate(response, context, learner_context)

            # Extract fields safely
            correctness = float(res_json.get("correctness", 0.5))
            correctness = max(0.0, min(1.0, correctness))

            classification = res_json.get("classification")
            if classification not in ["correct", "mostly_correct", "partially_correct", "incorrect", "ambiguous", "no_answer"]:
                if correctness >= 0.85:
                    classification = "correct"
                elif correctness >= 0.60:
                    classification = "mostly_correct"
                elif correctness >= 0.30:
                    classification = "partially_correct"
                else:
                    classification = "incorrect"

            concept_understanding = float(res_json.get("concept_understanding", correctness))
            concept_understanding = max(0.0, min(1.0, concept_understanding))

            confidence = float(res_json.get("confidence", 0.85))
            confidence = max(0.0, min(1.0, confidence))

            rq = res_json.get("reasoning_quality")
            reasoning_quality = float(rq) if rq is not None else None
            if reasoning_quality is not None:
                reasoning_quality = max(0.0, min(1.0, reasoning_quality))

            misc_data = res_json.get("misconception") or {}
            misconception = MisconceptionDetails(
                detected=bool(misc_data.get("detected", False)),
                type=misc_data.get("type"),
                description=misc_data.get("description"),
                confidence=float(misc_data.get("confidence", 0.0))
            )

            diff_adj = res_json.get("difficulty_adjustment", "maintain")
            if diff_adj not in ["decrease", "maintain", "increase"]:
                diff_adj = "maintain"

            evidence = res_json.get("evidence", [])
            if isinstance(evidence, str):
                evidence = [evidence]

            return EvaluationResult(
                question_id=context.question_id,
                correctness=correctness,
                classification=classification,
                confidence=confidence,
                concept=context.expected_concept,
                concept_understanding=concept_understanding,
                reasoning_quality=reasoning_quality,
                misconception=misconception,
                knowledge_gap=res_json.get("knowledge_gap", []),
                recommended_action=res_json.get("recommended_action", "CONTINUE" if correctness >= 0.85 else "RE_EXPLAIN"),
                recommended_strategy=res_json.get("recommended_strategy"),
                difficulty_adjustment=diff_adj,
                difficulty_delta=float(res_json.get("difficulty_delta", 0.0)),
                follow_up_required=bool(res_json.get("follow_up_required", correctness < 0.85)),
                follow_up_focus=res_json.get("follow_up_focus"),
                evidence=evidence,
                evaluation_status="success"
            )

        except Exception as e:
            logger.error(f"Error during LLM evaluation: {e}. Executing deterministic fallback.")
            fallback_res = deterministic_evaluator.evaluate(response, context, learner_context)
            fallback_res.evaluation_status = "unavailable"
            return fallback_res


llm_evaluator = LLMResponseEvaluator()
