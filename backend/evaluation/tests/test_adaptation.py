"""
Tests for Pedagogical Adaptation Engine.
Conforms to Sections 14, 15, 16, 17, 18, 19, 20, 21, 46, and 47.
"""

import pytest
from backend.evaluation.schemas import (
    EvaluationResult,
    QuestionContext,
    MisconceptionDetails,
)
from backend.evaluation.adaptation import adaptation_engine, get_next_strategy


def test_strategy_switching_section_16():
    """
    Section 16: Strategy switching.
    If previous strategy was formula, engine chooses a different strategy (e.g. analogy, visual).
    """
    next_s1 = get_next_strategy(["formula_derivation"])
    assert next_s1 in ["analogy", "visual", "worked_example"]

    next_s2 = get_next_strategy(["formula_derivation", "analogy"])
    assert next_s2 in ["visual", "worked_example", "step_by_step"]
    assert next_s2 != "analogy"
    assert next_s2 != "formula_derivation"


def test_repeated_failure_progression_section_20_and_46():
    """
    Section 46: Repeated Misconception / Failure Test.
    Simulate Question 1 (fail), Question 2 (fail), Question 3 (fail).
    The system MUST NOT repeatedly produce identical re-explain decisions.
    It MUST recommend: review prerequisite or simplify substantially.
    """
    ctx = QuestionContext(
        question_id="q_fail",
        question_text="Advanced circuit problem",
        expected_concept="circuit_analysis",
        prerequisite_concepts=["basic_ohms_law"],
        difficulty=0.6
    )

    eval_1 = EvaluationResult(
        question_id="q1",
        correctness=0.1,
        classification="incorrect",
        concept="circuit_analysis",
        concept_understanding=0.15,
        misconception=MisconceptionDetails(detected=True, type="inverse_relationship_confusion"),
        recommended_strategy="analogy"
    )

    eval_2 = EvaluationResult(
        question_id="q2",
        correctness=0.2,
        classification="incorrect",
        concept="circuit_analysis",
        concept_understanding=0.20,
        misconception=MisconceptionDetails(detected=True, type="calculation_error"),
        recommended_strategy="worked_example"
    )

    eval_3 = EvaluationResult(
        question_id="q3",
        correctness=0.1,
        classification="incorrect",
        concept="circuit_analysis",
        concept_understanding=0.10,
        misconception=MisconceptionDetails(detected=True, type="reasoning_error")
    )

    decision = adaptation_engine.decide(
        evaluation=eval_3,
        recent_evaluations=[eval_1, eval_2],
        question_context=ctx
    )

    assert decision.action == "REVIEW_PREREQUISITE"
    assert decision.prerequisite_to_review == "basic_ohms_law"
    assert decision.difficulty_adjustment == "decrease"
    assert decision.difficulty_delta < 0
    assert decision.follow_up.required is True


def test_repeated_success_progression_section_21_and_47():
    """
    Section 47: Success Progression Test.
    Simulate Question 1 (correct), Question 2 (correct), Question 3 (correct).
    System recommends: increase difficulty or move to application.
    """
    ctx = QuestionContext(
        question_id="q_success",
        question_text="Ohm's law problem",
        expected_concept="ohms_law",
        difficulty=0.4
    )

    eval_1 = EvaluationResult(
        question_id="q1",
        correctness=1.0,
        classification="correct",
        concept="ohms_law",
        concept_understanding=0.9
    )
    eval_2 = EvaluationResult(
        question_id="q2",
        correctness=0.95,
        classification="correct",
        concept="ohms_law",
        concept_understanding=0.95
    )
    eval_3 = EvaluationResult(
        question_id="q3",
        correctness=1.0,
        classification="correct",
        concept="ohms_law",
        concept_understanding=0.98
    )

    decision = adaptation_engine.decide(
        evaluation=eval_3,
        recent_evaluations=[eval_1, eval_2],
        question_context=ctx
    )

    assert decision.action == "INCREASE_DIFFICULTY"
    assert decision.difficulty_adjustment == "increase"
    assert decision.difficulty_delta > 0
    assert decision.target_difficulty > 0.4
