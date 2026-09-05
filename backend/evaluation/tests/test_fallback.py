"""
Tests for LLM Evaluator Fallback, Timeout, and Malformed Response Resilience.
Conforms to Sections 54, 55, and 57.
"""

import pytest
from unittest.mock import patch
from backend.evaluation.schemas import StudentResponse, QuestionContext
from backend.evaluation.evaluators import llm_evaluator


def test_llm_evaluator_malformed_json_fallback():
    """
    Section 54: If LLM returns malformed string or non-JSON,
    system must fall back gracefully without crashing.
    """
    ctx = QuestionContext(
        question_id="q_fb",
        question_text="Explain why resistance opposes electron flow.",
        expected_concept="resistance_mechanism",
        expected_answer="Electrons collide with lattice ions."
    )
    resp = StudentResponse(
        session_id="sess_fb",
        question_id="q_fb",
        student_answer="Electrons bump into atoms in the metal wire."
    )

    # Mock llm_service.generate_json to simulate parse failure
    with patch("backend.app.services.llm_service.llm_service.generate_json", return_value=None):
        res = llm_evaluator.evaluate(resp, ctx)
        assert res is not None
        assert res.evaluation_status in ["success", "unavailable"]
        assert 0.0 <= res.correctness <= 1.0


def test_llm_evaluator_exception_fallback():
    """
    Section 54: If LLM raises network timeout or API exception,
    system falls back deterministically and logs warning.
    """
    ctx = QuestionContext(
        question_id="q_fb2",
        question_text="What is Ohm's law?",
        expected_concept="ohms_law",
        expected_answer="V = I * R"
    )
    resp = StudentResponse(
        session_id="sess_fb2",
        question_id="q_fb2",
        student_answer="V = I * R"
    )

    with patch("backend.app.services.llm_service.llm_service.generate_json", side_effect=TimeoutError("Network timeout")):
        res = llm_evaluator.evaluate(resp, ctx)
        assert res is not None
        assert res.evaluation_status == "unavailable"
        assert res.correctness >= 0.85
