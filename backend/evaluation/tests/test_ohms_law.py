"""
Mandatory Canonical Integration Tests for Ohm's Law Scenarios.
Conforms to Sections 43, 44, 58, 59, and 60.
"""

import pytest
from backend.evaluation.schemas import StudentResponse, QuestionContext
from backend.evaluation.services import evaluation_service


def test_section_43_mandatory_ohms_law_misconception():
    """
    SECTION 43 MANDATORY TEST:
    Question:
    "If voltage remains constant and resistance increases, what happens to current?"

    Expected concept:
    Ohm's law: V = I * R, equivalent to I = V / R.

    Student answer:
    "Current increases."

    The evaluator should identify:
    - classification: incorrect
    - misconception: direct proportionality between resistance and current under constant voltage
    - knowledge gap: inverse relationship
    - recommended action: re_explain
    - recommended strategy: analogy
    - difficulty: decrease
    - follow_up_required: true
    """
    ctx = QuestionContext(
        question_id="ohm_mandatory_q1",
        question_text="If voltage remains constant and resistance increases, what happens to current?",
        expected_concept="ohms_law_inverse_proportionality",
        expected_answer="Current decreases because I = V / R under constant voltage."
    )
    resp = StudentResponse(
        session_id="sess_mandatory_1",
        question_id="ohm_mandatory_q1",
        student_answer="Current increases."
    )

    evaluation, adaptation, evidence = evaluation_service.evaluate_and_adapt(resp, ctx)

    # 1. Classification & Correctness
    assert evaluation.correctness < 0.30
    assert evaluation.classification == "incorrect"
    assert evaluation.confidence >= 0.90

    # 2. Misconception & Knowledge Gap
    assert evaluation.misconception.detected is True
    assert evaluation.misconception.type == "inverse_relationship_confusion"
    assert "proportionality" in evaluation.misconception.description.lower()
    assert any("inverse" in gap.lower() for gap in evaluation.knowledge_gap)

    # 3. Adaptation Decision
    assert adaptation.action in ["RE_EXPLAIN", "USE_ANALOGY"]
    assert adaptation.strategy == "analogy"
    assert adaptation.difficulty_adjustment == "decrease"
    assert adaptation.difficulty_delta < 0
    assert adaptation.question_after_reteach is True

    # 4. Targeted Follow-up Probe Recommendation
    assert adaptation.follow_up.required is True
    assert "inverse" in adaptation.follow_up.focus.lower() or "proportionality" in adaptation.follow_up.focus.lower()


def test_section_44_second_mandatory_ohms_law_numerical():
    """
    SECTION 44 SECOND MANDATORY TEST:
    Question:
    "If voltage is 10 V and resistance is 5 Ω, what is current?"

    Expected:
    2 A

    Student:
    "2 A"

    Expected:
    - correctness high
    - concept understanding high
    - recommended action: continue
    - Do NOT unnecessarily reteach the concept.
    """
    ctx = QuestionContext(
        question_id="ohm_mandatory_q2",
        question_text="If voltage is 10 V and resistance is 5 Ω, what is current?",
        expected_concept="ohms_law_calculation",
        expected_answer="2 A"
    )
    resp = StudentResponse(
        session_id="sess_mandatory_2",
        question_id="ohm_mandatory_q2",
        student_answer="2 A",
        answer_type="numerical"
    )

    evaluation, adaptation, evidence = evaluation_service.evaluate_and_adapt(resp, ctx)

    # 1. Correctness & Understanding
    assert evaluation.correctness >= 0.95
    assert evaluation.classification == "correct"
    assert evaluation.concept_understanding >= 0.90
    assert evaluation.misconception.detected is False

    # 2. Action: Must NOT reteach
    assert adaptation.action in ["CONTINUE", "INCREASE_DIFFICULTY"]
    assert adaptation.action != "RE_EXPLAIN"
    assert adaptation.action != "USE_ANALOGY"
    assert adaptation.difficulty_adjustment in ["maintain", "increase"]
