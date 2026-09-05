"""
Tests for Multilingual and Hinglish Response Evaluation.
Conforms to Sections 29, 50, and 57.
"""

import pytest
from backend.evaluation.schemas import StudentResponse, QuestionContext
from backend.evaluation.evaluators import deterministic_evaluator


def test_hinglish_response_evaluation_section_50():
    """
    Section 50 Mandatory Language Test:
    Question: "What happens to current when resistance increases at constant voltage?"
    Student: "Resistance badhne par current decrease hota hai."
    Expected:
    - Semantically correct.
    - Hinglish is NOT penalized.
    - classification = "correct"
    """
    ctx = QuestionContext(
        question_id="q_lang",
        question_text="What happens to current when resistance increases at constant voltage?",
        expected_concept="ohms_law",
        expected_answer="Current decreases."
    )

    hinglish_variants = [
        "Resistance badhne par current decrease hota hai.",
        "Current kam ho jayega kyunki resistance oppose karta hai.",
        "Current ghatega.",
        "Jab resistance badhta hai toh current kam hota hai."
    ]

    for ans in hinglish_variants:
        resp = StudentResponse(
            session_id="sess_lang",
            question_id="q_lang",
            student_answer=ans,
            language="Hinglish"
        )
        res = deterministic_evaluator.evaluate(resp, ctx)
        assert res.correctness >= 0.85
        assert res.classification == "correct"
        assert res.misconception.detected is False
        assert res.recommended_action == "CONTINUE"
