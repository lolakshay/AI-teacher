"""
Tests for Multiple Choice Question (MCQ) deterministic evaluation.
Conforms to Sections 10, 32, and 57.
"""

import pytest
from backend.evaluation.schemas import StudentResponse, QuestionContext
from backend.evaluation.evaluators import deterministic_evaluator


def test_mcq_exact_letter_correct():
    ctx = QuestionContext(
        question_id="mcq_1",
        question_text="What happens to current if resistance increases at constant voltage?",
        options=["A) Current increases", "B) Current decreases", "C) Stays constant", "D) Becomes zero"],
        correct_option="B",
        expected_concept="ohms_law"
    )
    resp = StudentResponse(
        session_id="sess_1",
        question_id="mcq_1",
        student_answer="B",
        answer_type="mcq"
    )

    result = deterministic_evaluator.evaluate(resp, ctx)
    assert result.correctness == 1.0
    assert result.classification == "correct"
    assert result.confidence == 1.0
    assert result.reasoning_quality is None
    assert result.recommended_action == "CONTINUE"
    assert result.misconception.detected is False


def test_mcq_letter_variations_correct():
    ctx = QuestionContext(
        question_id="mcq_2",
        question_text="Select the correct unit of electrical resistance:",
        options=["A) Volt", "B) Ampere", "C) Ohm", "D) Watt"],
        correct_option="C",
        expected_concept="resistance_units"
    )

    for answer_variant in ["(c)", "Option C", "C)", "c", "Ohm"]:
        resp = StudentResponse(
            session_id="sess_1",
            question_id="mcq_2",
            student_answer=answer_variant,
            answer_type="mcq"
        )
        res = deterministic_evaluator.evaluate(resp, ctx)
        assert res.correctness == 1.0
        assert res.classification == "correct"


def test_mcq_incorrect():
    ctx = QuestionContext(
        question_id="mcq_3",
        question_text="What happens to current if resistance increases at constant voltage?",
        options=["A) Current increases", "B) Current decreases", "C) Stays constant"],
        correct_option="B",
        expected_concept="ohms_law"
    )
    resp = StudentResponse(
        session_id="sess_1",
        question_id="mcq_3",
        student_answer="A",
        answer_type="mcq"
    )

    result = deterministic_evaluator.evaluate(resp, ctx)
    assert result.correctness == 0.0
    assert result.classification == "incorrect"
    assert result.confidence == 1.0
    assert result.reasoning_quality is None
    assert result.misconception.detected is True
    assert result.recommended_action in ["RE_EXPLAIN", "give_analogy"]
