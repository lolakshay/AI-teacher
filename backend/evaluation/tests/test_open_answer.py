"""
Tests for Open-Ended, Partial Correctness, Ambiguous, and No-Answer Responses.
Conforms to Sections 8, 9, 36, 37, 45, 48, and 49.
"""

import pytest
from backend.evaluation.schemas import StudentResponse, QuestionContext
from backend.evaluation.evaluators import deterministic_evaluator


def test_partial_understanding_test_section_45():
    """
    Section 45 Mandatory Partial Credit Scenario:
    Question: "Why does increasing resistance reduce current when voltage is constant?"
    Student: "Resistance opposes current."
    Expected:
    - Graded correctness (0.30 - 0.59)
    - Concept understanding (~0.60)
    - Action: CLARIFY or SHOW_WORKED_EXAMPLE
    - NOT marked completely incorrect, NOT marked fully correct.
    """
    ctx = QuestionContext(
        question_id="q_partial",
        question_text="Why does increasing resistance reduce current when voltage is constant?",
        expected_concept="resistance_opposition",
        expected_answer="Current is inversely proportional to resistance (I = V / R) under constant voltage."
    )
    resp = StudentResponse(
        session_id="sess_partial",
        question_id="q_partial",
        student_answer="Resistance opposes current."
    )

    res = deterministic_evaluator.evaluate(resp, ctx)
    assert 0.30 <= res.correctness <= 0.60
    assert res.classification == "partially_correct"
    assert res.concept_understanding >= 0.50
    assert res.misconception.detected is False
    assert res.recommended_action in ["CLARIFY", "SHOW_WORKED_EXAMPLE"]
    assert res.follow_up_required is True


def test_no_answer_responses_section_48():
    """
    Section 48 Mandatory No-Answer Test:
    Student: "I don't know." / "Skip" / "pata nahi"
    Expected:
    - classification = "no_answer"
    - misconception.detected = False (DO NOT claim a misconception)
    - recommended_action = "SIMPLIFY"
    """
    ctx = QuestionContext(
        question_id="q_no_ans",
        question_text="Explain how a capacitor stores energy.",
        expected_concept="capacitance"
    )

    for no_ans_text in ["I don't know.", "Skip", "idk", "pata nahi", "No idea"]:
        resp = StudentResponse(
            session_id="sess_no_ans",
            question_id="q_no_ans",
            student_answer=no_ans_text
        )
        res = deterministic_evaluator.evaluate(resp, ctx)
        assert res.correctness == 0.0
        assert res.classification == "no_answer"
        assert res.misconception.detected is False
        assert res.recommended_action == "SIMPLIFY"
        assert res.difficulty_adjustment == "decrease"


def test_ambiguous_responses_section_49():
    """
    Section 49 Mandatory Ambiguous Test:
    Student: "It depends."
    Expected:
    - classification = "ambiguous"
    - recommended_action = "ASK_FOLLOWUP"
    - follow_up_required = True
    """
    ctx = QuestionContext(
        question_id="q_ambig",
        question_text="Will adding another resistor in a circuit always decrease the current?",
        expected_concept="series_vs_parallel_resistors"
    )

    for ambig_text in ["It depends.", "Maybe", "Depends on condition", "Ho bhi sakta hai"]:
        resp = StudentResponse(
            session_id="sess_ambig",
            question_id="q_ambig",
            student_answer=ambig_text
        )
        res = deterministic_evaluator.evaluate(resp, ctx)
        assert res.classification == "ambiguous"
        assert res.recommended_action == "ASK_FOLLOWUP"
        assert res.follow_up_required is True
        assert res.misconception.detected is False
