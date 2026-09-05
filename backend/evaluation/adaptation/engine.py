"""
Adaptation Engine for Agent 6.
Conforms to Sections 3, 14, 15, 16, 17, 18, 19, 20, 21, 38.
"""

from typing import List, Optional, Dict, Any
from backend.evaluation.schemas import (
    EvaluationResult,
    QuestionContext,
    AdaptationDecision,
    AdaptationAction,
    FollowUpRecommendation,
)
from backend.evaluation.adaptation.rules import (
    CORRECTNESS_STRONG_THRESHOLD,
    CORRECTNESS_MODERATE_THRESHOLD,
    CORRECTNESS_PARTIAL_THRESHOLD,
    get_next_strategy,
)


class AdaptationEngine:
    """
    Decoupled pedagogical adaptation engine.
    Given diagnostic evaluation evidence and session history,
    computes actionable recommendations for Agent 1 (Teaching Orchestrator).
    """

    def decide(
        self,
        evaluation: EvaluationResult,
        recent_evaluations: Optional[List[EvaluationResult]] = None,
        question_context: Optional[QuestionContext] = None,
        learner_context: Optional[Dict[str, Any]] = None
    ) -> AdaptationDecision:
        history = recent_evaluations or []
        concept = evaluation.concept or (question_context.expected_concept if question_context else "current_topic")
        current_difficulty = question_context.difficulty if question_context else 0.5

        # -------------------------------------------------------------
        # 1. REPEATED FAILURE DETECTION (Section 20 & 46)
        # -------------------------------------------------------------
        concept_history = [e for e in history if e.concept == concept or not e.concept]
        recent_scores = [e.correctness for e in concept_history[-2:]] + [evaluation.correctness]

        if len(recent_scores) >= 3 and all(s < CORRECTNESS_PARTIAL_THRESHOLD for s in recent_scores):
            # 3 consecutive failures: Trigger prerequisite review or deep simplification
            prereq = None
            if question_context and question_context.prerequisite_concepts:
                prereq = question_context.prerequisite_concepts[0]

            action: AdaptationAction = "REVIEW_PREREQUISITE" if prereq else "SIMPLIFY"
            strategy = "step_by_step" if prereq else "simplification"

            return AdaptationDecision(
                action=action,
                focus_concept=prereq or concept,
                strategy=strategy,
                difficulty_adjustment="decrease",
                difficulty_delta=-0.15,
                target_difficulty=max(0.1, round(current_difficulty - 0.15, 2)),
                question_after_reteach=True,
                prerequisite_to_review=prereq,
                follow_up=FollowUpRecommendation(
                    required=True,
                    concept=prereq or concept,
                    difficulty=max(0.1, round(current_difficulty - 0.15, 2)),
                    question_type="conceptual",
                    focus=f"Foundational understanding of {prereq or concept}",
                    reason="Verify student grasp of prerequisite before re-attempting composite concept."
                ),
                reason=f"Student experienced 3 consecutive difficulties on {concept}. Reverting to prerequisite grounding."
            )

        # -------------------------------------------------------------
        # 2. REPEATED SUCCESS DETECTION (Section 21 & 47)
        # -------------------------------------------------------------
        if len(recent_scores) >= 3 and all(s >= CORRECTNESS_STRONG_THRESHOLD for s in recent_scores):
            # 3 consecutive successes: Advance to higher difficulty or application
            return AdaptationDecision(
                action="INCREASE_DIFFICULTY",
                focus_concept=concept,
                strategy="worked_example",
                difficulty_adjustment="increase",
                difficulty_delta=+0.1,
                target_difficulty=min(1.0, round(current_difficulty + 0.1, 2)),
                question_after_reteach=False,
                follow_up=FollowUpRecommendation(
                    required=False,
                    concept=concept,
                    difficulty=min(1.0, round(current_difficulty + 0.1, 2)),
                    question_type="application",
                    focus="Advanced real-world application or problem solving",
                    reason="Student has demonstrated sustained mastery."
                ),
                reason=f"Student achieved sustained mastery across 3 consecutive questions on {concept}. Elevating challenge."
            )

        # -------------------------------------------------------------
        # 3. SPECIAL CLASSIFICATIONS (No-Answer / Ambiguous)
        # -------------------------------------------------------------
        if evaluation.classification == "no_answer":
            return AdaptationDecision(
                action="SIMPLIFY",
                focus_concept=concept,
                strategy="simplification",
                difficulty_adjustment="decrease",
                difficulty_delta=-0.1,
                target_difficulty=max(0.1, round(current_difficulty - 0.1, 2)),
                question_after_reteach=True,
                follow_up=FollowUpRecommendation(
                    required=True,
                    concept=concept,
                    difficulty=max(0.1, round(current_difficulty - 0.1, 2)),
                    question_type="conceptual",
                    focus="Core definition probe",
                    reason="Check comprehension following simplified explanation."
                ),
                reason="Student indicated uncertainty or skipped; presenting simplified foundational view."
            )

        if evaluation.classification == "ambiguous":
            return AdaptationDecision(
                action="ASK_FOLLOWUP",
                focus_concept=concept,
                strategy="step_by_step",
                difficulty_adjustment="maintain",
                difficulty_delta=0.0,
                target_difficulty=current_difficulty,
                question_after_reteach=False,
                follow_up=FollowUpRecommendation(
                    required=True,
                    concept=concept,
                    difficulty=current_difficulty,
                    question_type="conceptual",
                    focus=evaluation.follow_up_focus or "Clarify assumptions and reasoning",
                    reason="Probe ambiguous student response to determine true understanding."
                ),
                reason="Response was ambiguous; asking clarifying follow-up question."
            )

        # -------------------------------------------------------------
        # 4. MISCONCEPTION / RETEACHING WITH STRATEGY SHIFT (Section 16)
        # -------------------------------------------------------------
        if evaluation.misconception.detected:
            # Determine past strategies used to ensure we choose a NEW one
            past_strategies = [
                e.recommended_strategy for e in history if e.recommended_strategy
            ]
            if evaluation.recommended_strategy:
                # If evaluator explicitly recommended a strategy, evaluate if it's new
                strat = evaluation.recommended_strategy
            else:
                strat = get_next_strategy(past_strategies)

            return AdaptationDecision(
                action="RE_EXPLAIN",
                focus_concept=evaluation.follow_up_focus or concept,
                strategy=strat,
                difficulty_adjustment="decrease",
                difficulty_delta=-0.1,
                target_difficulty=max(0.1, round(current_difficulty - 0.1, 2)),
                question_after_reteach=True,
                follow_up=FollowUpRecommendation(
                    required=True,
                    concept=concept,
                    difficulty=max(0.1, round(current_difficulty - 0.1, 2)),
                    question_type="conceptual",
                    focus=f"Resolve {evaluation.misconception.type or 'misconception'}",
                    reason="Verify corrected mental model after alternative explanation."
                ),
                reason=(
                    f"Detected misconception '{evaluation.misconception.description or evaluation.misconception.type}'. "
                    f"Switching pedagogical strategy to '{strat}' to reconstruct mental model."
                )
            )

        # -------------------------------------------------------------
        # 5. GRADED UNDERSTANDING BRANCHES (Section 7, 15)
        # -------------------------------------------------------------
        if evaluation.correctness >= CORRECTNESS_STRONG_THRESHOLD:
            # High understanding (>= 0.85) -> CONTINUE
            return AdaptationDecision(
                action="CONTINUE",
                focus_concept=concept,
                strategy=None,
                difficulty_adjustment="maintain",
                difficulty_delta=0.0,
                target_difficulty=current_difficulty,
                question_after_reteach=False,
                follow_up=FollowUpRecommendation(required=False),
                reason="Student demonstrated strong conceptual understanding. Advancing."
            )

        elif evaluation.correctness >= CORRECTNESS_MODERATE_THRESHOLD:
            # Mostly correct (0.60 - 0.84) -> CLARIFY + FOLLOWUP
            return AdaptationDecision(
                action="CLARIFY",
                focus_concept=concept,
                strategy="step_by_step",
                difficulty_adjustment="maintain",
                difficulty_delta=0.0,
                target_difficulty=current_difficulty,
                question_after_reteach=True,
                follow_up=FollowUpRecommendation(
                    required=True,
                    concept=concept,
                    difficulty=current_difficulty,
                    question_type="conceptual",
                    focus=evaluation.follow_up_focus or "Minor gap clarification",
                    reason="Reinforce minor conceptual nuances."
                ),
                reason="Minor gap identified in otherwise sound reasoning; providing brief clarification."
            )

        elif evaluation.correctness >= CORRECTNESS_PARTIAL_THRESHOLD:
            # Partially correct (0.30 - 0.59) -> SIMPLIFY or SHOW_WORKED_EXAMPLE
            return AdaptationDecision(
                action="SHOW_WORKED_EXAMPLE",
                focus_concept=concept,
                strategy="worked_example",
                difficulty_adjustment="maintain",
                difficulty_delta=0.0,
                target_difficulty=current_difficulty,
                question_after_reteach=True,
                follow_up=FollowUpRecommendation(
                    required=True,
                    concept=concept,
                    difficulty=current_difficulty,
                    question_type="conceptual",
                    focus="Step-by-step example verification",
                    reason="Solidify partial intuition into comprehensive understanding."
                ),
                reason="Student has partial intuition; providing a worked example to bridge the gap."
            )

        else:
            # Incorrect / major misunderstanding (< 0.30) without explicit named misconception
            return AdaptationDecision(
                action="RE_EXPLAIN",
                focus_concept=concept,
                strategy="analogy",
                difficulty_adjustment="decrease",
                difficulty_delta=-0.1,
                target_difficulty=max(0.1, round(current_difficulty - 0.1, 2)),
                question_after_reteach=True,
                follow_up=FollowUpRecommendation(
                    required=True,
                    concept=concept,
                    difficulty=max(0.1, round(current_difficulty - 0.1, 2)),
                    question_type="conceptual",
                    focus=concept,
                    reason="Verify concept re-explanation."
                ),
                reason="Significant conceptual gap detected; re-explaining using intuitive analogy."
            )


adaptation_engine = AdaptationEngine()
