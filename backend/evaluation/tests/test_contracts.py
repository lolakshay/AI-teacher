"""
Tests for Integration Contracts with Agent 1 (Orchestrator) and Agent 3 (Personalization).
Conforms to Sections 22, 23, 40, 41, and 57.
"""

import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.evaluation.schemas import (
    StudentResponse,
    QuestionContext,
    LearningEvidence,
)
from backend.evaluation.services import evaluation_service
from backend.personalization.service import personalization_service

client = TestClient(app)


def test_agent_1_integration_contract():
    """
    Section 40: Agent 1 Orchestrator calls evaluate_simple or evaluate_and_adapt
    and directly receives EvaluationResult + AdaptationDecision without parsing LLM strings.
    """
    eval_res, adapt_dec = evaluation_service.evaluate_simple(
        question_text="If voltage remains constant and resistance increases, what happens to current?",
        student_answer="Current increases.",
        expected_concept="ohms_law",
        expected_answer="Current decreases."
    )

    assert eval_res.correctness < 0.30
    assert eval_res.misconception.detected is True
    assert adapt_dec.action in ["RE_EXPLAIN", "USE_ANALOGY"]
    assert adapt_dec.strategy == "analogy"
    assert adapt_dec.difficulty_adjustment == "decrease"
    assert adapt_dec.follow_up.required is True


def test_agent_3_evidence_contract():
    """
    Section 23 & 41: Agent 6 produces structured LearningEvidence and submits it
    to Agent 3 PersonalizationService.update_concept_knowledge. Agent 3 updates durable profile.
    """
    student_id = "test_agent3_contract_student"
    concept_id = "ohms_law_proportionality"

    resp = StudentResponse(
        session_id="sess_contract",
        question_id="q_contract",
        student_answer="Current increases."
    )
    ctx = QuestionContext(
        question_id="q_contract",
        question_text="If voltage is constant and resistance increases, what happens to current?",
        expected_concept=concept_id,
        expected_answer="Current decreases."
    )

    evaluation, adaptation, evidence = evaluation_service.evaluate_and_adapt(
        response=resp,
        question=ctx,
        student_id=student_id,
        auto_submit_to_agent3=True
    )

    assert isinstance(evidence, LearningEvidence)
    assert evidence.student_id == student_id
    assert evidence.concept == concept_id
    assert evidence.misconception_detected is True

    # Verify Agent 3 updated profile correctly
    profile = personalization_service.get_profile(student_id)
    assert profile is not None
    # Check that concept mastery reflects the evidence
    assert concept_id in profile.concept_mastery
    knowledge = profile.concept_mastery[concept_id]
    assert knowledge.incorrect_attempts >= 1
    assert len(knowledge.misconceptions) >= 1


def test_rest_api_respond_endpoint():
    """
    Section 39: Test POST /api/evaluation/respond
    """
    payload = {
        "student_response": {
            "session_id": "sess_api_test",
            "question_id": "q_api_test",
            "student_answer": "Current increases.",
            "answer_type": "short_answer"
        },
        "question_context": {
            "question_id": "q_api_test",
            "question_text": "If voltage remains constant and resistance increases, what happens to current?",
            "expected_concept": "ohms_law",
            "expected_answer": "Current decreases."
        }
    }

    response = client.post("/api/evaluation/respond", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["evaluation"]["misconception"]["detected"] is True
    assert data["adaptation"]["action"] in ["RE_EXPLAIN", "USE_ANALOGY"]
    assert data["learning_evidence"]["concept"] == "ohms_law"


def test_rest_api_get_by_id_and_session():
    """
    Section 39: Test GET /api/evaluation/{id} and GET /api/evaluation/session/{session_id}
    """
    session_id = "sess_query_test"
    resp = StudentResponse(
        session_id=session_id,
        question_id="q_query",
        student_answer="Current decreases."
    )
    ctx = QuestionContext(
        question_id="q_query",
        question_text="If voltage is constant and resistance increases, what happens to current?",
        expected_concept="ohms_law",
        expected_answer="Current decreases."
    )
    eval_res, _, _ = evaluation_service.evaluate_and_adapt(resp, ctx)

    # 1. Query by ID
    get_res = client.get(f"/api/evaluation/{eval_res.evaluation_id}")
    assert get_res.status_code == 200
    assert get_res.json()["evaluation_id"] == eval_res.evaluation_id

    # 2. Query by Session
    sess_res = client.get(f"/api/evaluation/session/{session_id}")
    assert sess_res.status_code == 200
    evals = sess_res.json()
    assert len(evals) >= 1
    assert any(e["evaluation_id"] == eval_res.evaluation_id for e in evals)
