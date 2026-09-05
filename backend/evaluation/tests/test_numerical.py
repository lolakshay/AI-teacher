"""
Tests for Numerical Response Evaluation with Tolerance and Unit Verification.
Conforms to Sections 31, 44, and 57.
"""

import pytest
from backend.evaluation.schemas import (
    StudentResponse,
    QuestionContext,
    NumericalToleranceConfig,
)
from backend.evaluation.evaluators import deterministic_evaluator


def test_numerical_exact_with_unit():
    ctx = QuestionContext(
        question_id="num_1",
        question_text="If voltage is 10 V and resistance is 5 Ω, calculate the current:",
        expected_answer="2 A",
        expected_concept="ohms_law_calculation",
        numerical_config=NumericalToleranceConfig(
            tolerance_type="relative",
            tolerance_value=0.05,
            expected_unit="A",
            require_unit=True
        )
    )
    resp = StudentResponse(
        session_id="sess_num",
        question_id="num_1",
        student_answer="2 A",
        answer_type="numerical"
    )

    res = deterministic_evaluator.evaluate(resp, ctx)
    assert res.correctness == 1.0
    assert res.classification == "correct"
    assert res.misconception.detected is False
    assert res.concept_understanding >= 0.90


def test_numerical_within_tolerance():
    # Acceleration due to gravity: 9.81 expected, 9.8 given (within 5%)
    ctx = QuestionContext(
        question_id="num_2",
        question_text="What is the approximate standard acceleration due to gravity near Earth's surface?",
        expected_answer="9.81 m/s^2",
        expected_concept="gravitational_acceleration",
        numerical_config=NumericalToleranceConfig(
            tolerance_type="relative",
            tolerance_value=0.05,
            expected_unit="m/s^2",
            require_unit=False
        )
    )
    resp = StudentResponse(
        session_id="sess_num",
        question_id="num_2",
        student_answer="9.8 m/s^2",
        answer_type="numerical"
    )

    res = deterministic_evaluator.evaluate(resp, ctx)
    assert res.correctness == 1.0
    assert res.classification == "correct"


def test_numerical_outside_tolerance():
    ctx = QuestionContext(
        question_id="num_3",
        question_text="If voltage is 10 V and resistance is 5 Ω, calculate current:",
        expected_answer="2 A",
        expected_concept="ohms_law_calculation",
        numerical_config=NumericalToleranceConfig(
            tolerance_type="relative",
            tolerance_value=0.05,
            expected_unit="A"
        )
    )
    resp = StudentResponse(
        session_id="sess_num",
        question_id="num_3",
        student_answer="4 A",
        answer_type="numerical"
    )

    res = deterministic_evaluator.evaluate(resp, ctx)
    assert res.correctness < 0.30
    assert res.classification == "incorrect"
    assert res.misconception.detected is True
    assert res.misconception.type == "calculation_error"


def test_numerical_missing_required_unit():
    ctx = QuestionContext(
        question_id="num_4",
        question_text="Calculate current for 10V and 5 Ohms:",
        expected_answer="2 A",
        expected_concept="ohms_law_calculation",
        numerical_config=NumericalToleranceConfig(
            tolerance_type="relative",
            tolerance_value=0.05,
            expected_unit="A",
            require_unit=True
        )
    )
    resp = StudentResponse(
        session_id="sess_num",
        question_id="num_4",
        student_answer="2",  # Missing 'A'
        answer_type="numerical"
    )

    res = deterministic_evaluator.evaluate(resp, ctx)
    assert res.correctness == 0.75  # Partial credit for correct magnitude
    assert res.classification == "mostly_correct"
    assert res.misconception.detected is True
    assert res.misconception.type == "unit_confusion"
    assert "units" in res.follow_up_focus.lower()


def test_numerical_fractions_and_scientific():
    ctx = QuestionContext(
        question_id="num_5",
        question_text="Calculate current if V=1V and R=2 Ohms:",
        expected_answer="0.5 A",
        expected_concept="ohms_law_calculation",
        numerical_config=NumericalToleranceConfig(expected_unit="A")
    )
    resp = StudentResponse(
        session_id="sess_num",
        question_id="num_5",
        student_answer="1/2 A",
        answer_type="numerical"
    )

    res = deterministic_evaluator.evaluate(resp, ctx)
    assert res.correctness == 1.0
    assert res.classification == "correct"
