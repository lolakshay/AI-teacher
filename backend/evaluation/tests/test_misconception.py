"""
Tests for Misconception Detection, Knowledge Gap Separation, and Confidence Estimation.
Conforms to Sections 11, 12, 13, and 35.
"""

import pytest
from backend.evaluation.schemas import StudentResponse, QuestionContext
from backend.evaluation.evaluators import deterministic_evaluator


def test_misconception_vs_knowledge_gap_distinction():
    """
    Section 13: Separate Misconception from Knowledge Gap.
    - Misconception: Student holds an active flawed mental model (e.g. 'Current increases with resistance').
    - Knowledge Gap: Student lacks definition or formula (e.g. 'I don't know what resistance means').
    """
    ctx = QuestionContext(
        question_id="q_gap_vs_misc",
        question_text="If voltage remains constant and resistance increases, what happens to current?",
        expected_concept="ohms_law"
    )

    # 1. Student with misconception
    resp_misc = StudentResponse(
        session_id="sess_dist",
        question_id="q_gap_vs_misc",
        student_answer="Current increases."
    )
    res_misc = deterministic_evaluator.evaluate(resp_misc, ctx)
    assert res_misc.misconception.detected is True
    assert res_misc.misconception.type == "inverse_relationship_confusion"
    assert res_misc.misconception.confidence >= 0.90
    assert len(res_misc.knowledge_gap) > 0

    # 2. Student with knowledge gap / no mental model
    resp_gap = StudentResponse(
        session_id="sess_dist",
        question_id="q_gap_vs_misc",
        student_answer="I don't know what resistance means."
    )
    res_gap = deterministic_evaluator.evaluate(resp_gap, ctx)
    assert res_gap.misconception.detected is False
    assert res_gap.classification == "no_answer"
    assert len(res_gap.knowledge_gap) > 0


def test_misconception_confidence_never_certain_when_ambiguous():
    """
    Section 12: Never claim a misconception with certainty when answer is ambiguous.
    """
    ctx = QuestionContext(
        question_id="q_uncertain",
        question_text="If resistance increases, what happens to current?",
        expected_concept="ohms_law"
    )
    resp = StudentResponse(
        session_id="sess_uncert",
        question_id="q_uncertain",
        student_answer="Maybe it depends on the wire."
    )
    res = deterministic_evaluator.evaluate(resp, ctx)
    assert res.misconception.detected is False
    assert res.misconception.confidence == 0.0
    assert res.classification == "ambiguous"
