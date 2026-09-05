"""
Response Evaluator and Adaptive Teaching Service for Agent 6.
Conforms to Sections 39, 40, 41, and 42.
"""

import logging
from typing import Dict, List, Optional, Tuple, Any, Union
from datetime import datetime, timezone

from backend.evaluation.schemas import (
    StudentResponse,
    QuestionContext,
    EvaluationResult,
    AdaptationDecision,
    LearningEvidence,
)
from backend.evaluation.evaluators import (
    deterministic_evaluator,
    llm_evaluator,
)
from backend.evaluation.adaptation import adaptation_engine

logger = logging.getLogger(__name__)


class ResponseEvaluatorService:
    """
    Central Coordinator for Agent 6.
    Provides clean integration points for:
    - Agent 1 (Teaching Orchestrator): evaluate_and_adapt(...)
    - Agent 3 (Personalization Engine): produces LearningEvidence
    - REST API Endpoints: query past evaluations by ID or session
    """

    def __init__(self):
        # In-memory storage for evaluations across active sessions
        self._evaluations_by_id: Dict[str, EvaluationResult] = {}
        self._evaluations_by_session: Dict[str, List[EvaluationResult]] = {}
        self._adaptations_by_id: Dict[str, AdaptationDecision] = {}

    def evaluate_and_adapt(
        self,
        response: StudentResponse,
        question: QuestionContext,
        learner_context: Optional[Dict[str, Any]] = None,
        student_id: Optional[str] = None,
        auto_submit_to_agent3: bool = False
    ) -> Tuple[EvaluationResult, AdaptationDecision, LearningEvidence]:
        """
        Primary end-to-end evaluation & adaptation flow:
        1. Evaluates student response using hybrid (deterministic or LLM) evaluator.
        2. Decides pedagogical adaptation using adaptation engine and session history.
        3. Generates clean LearningEvidence for Agent 3.
        4. Optionally forwards evidence to Agent 3's durable mastery model.
        """
        session_id = response.session_id
        session_history = self._evaluations_by_session.get(session_id, [])

        # -------------------------------------------------------------
        # STEP 1: HYBRID EVALUATION
        # -------------------------------------------------------------
        if deterministic_evaluator.can_evaluate(response, question):
            evaluation = deterministic_evaluator.evaluate(response, question, learner_context)
        else:
            evaluation = llm_evaluator.evaluate(response, question, learner_context)

        # -------------------------------------------------------------
        # STEP 2: PEDAGOGICAL ADAPTATION DECISION
        # -------------------------------------------------------------
        adaptation = adaptation_engine.decide(
            evaluation=evaluation,
            recent_evaluations=session_history,
            question_context=question,
            learner_context=learner_context
        )

        # -------------------------------------------------------------
        # STEP 3: CONSTRUCT LEARNING EVIDENCE FOR AGENT 3
        # -------------------------------------------------------------
        s_id = student_id or (learner_context.get("student_id") if learner_context else "unknown_student")
        evidence = LearningEvidence(
            student_id=s_id,
            session_id=session_id,
            question_id=response.question_id,
            concept=evaluation.concept or question.expected_concept,
            correctness=evaluation.correctness,
            concept_understanding=evaluation.concept_understanding,
            classification=evaluation.classification,
            misconception_detected=evaluation.misconception.detected,
            misconception_type=evaluation.misconception.type,
            misconception_description=evaluation.misconception.description,
            knowledge_gap=evaluation.knowledge_gap,
            confidence=evaluation.confidence,
            reasoning_quality=evaluation.reasoning_quality,
            timestamp=datetime.now(timezone.utc).isoformat(),
            details={
                "recommended_action": adaptation.action,
                "recommended_strategy": adaptation.strategy,
                "evidence_notes": evaluation.evidence
            }
        )

        # -------------------------------------------------------------
        # STEP 4: PERSIST IN-MEMORY HISTORY
        # -------------------------------------------------------------
        self._evaluations_by_id[evaluation.evaluation_id] = evaluation
        self._adaptations_by_id[evaluation.evaluation_id] = adaptation

        if session_id not in self._evaluations_by_session:
            self._evaluations_by_session[session_id] = []
        self._evaluations_by_session[session_id].append(evaluation)

        # -------------------------------------------------------------
        # STEP 5: OPTIONAL FORWARDING TO AGENT 3
        # -------------------------------------------------------------
        if auto_submit_to_agent3:
            self._submit_to_agent3(evidence)

        return evaluation, adaptation, evidence

    def evaluate_simple(
        self,
        question_text: str,
        student_answer: str,
        expected_concept: str = "",
        expected_answer: str = "",
        session_id: str = "session_default",
        question_id: str = "q_default",
        learner_context: Optional[Dict[str, Any]] = None,
        difficulty: float = 0.5
    ) -> Tuple[EvaluationResult, AdaptationDecision]:
        """
        Convenience method for Agent 1 or lightweight callers.
        """
        resp = StudentResponse(
            session_id=session_id,
            question_id=question_id,
            student_answer=student_answer
        )
        ctx = QuestionContext(
            question_id=question_id,
            question_text=question_text,
            expected_concept=expected_concept,
            expected_answer=expected_answer,
            difficulty=difficulty
        )
        eval_res, adapt_dec, _ = self.evaluate_and_adapt(resp, ctx, learner_context)
        return eval_res, adapt_dec

    def get_evaluation(self, evaluation_id: str) -> Optional[EvaluationResult]:
        return self._evaluations_by_id.get(evaluation_id)

    def get_adaptation(self, evaluation_id: str) -> Optional[AdaptationDecision]:
        return self._adaptations_by_id.get(evaluation_id)

    def get_session_evaluations(self, session_id: str) -> List[EvaluationResult]:
        return self._evaluations_by_session.get(session_id, [])

    def _submit_to_agent3(self, evidence: LearningEvidence) -> None:
        """Safe submission to Agent 3 Personalization Service."""
        try:
            from backend.personalization.service import personalization_service
            personalization_service.update_concept_knowledge(
                student_id=evidence.student_id,
                concept_id=evidence.concept,
                evidence=evidence.to_agent3_payload()
            )
            logger.info(f"Submitted learning evidence for {evidence.concept} to Agent 3.")
        except Exception as e:
            logger.warning(f"Could not submit evidence to Agent 3: {e}")


evaluation_service = ResponseEvaluatorService()
