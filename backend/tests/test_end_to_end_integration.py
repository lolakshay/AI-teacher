"""
Integration & End-to-End Test Suite for AI Teacher Subsystem
Owned by AGENT 10 — Integration, Demo Orchestration + Documentation.

Verifies:
1. test_full_ai_teacher_flow (Section 32: 22-Step Lifecycle)
2. test_golden_path_ohms_law (Section 33: Golden Path Acceptance Test)
3. test_loop_protection (Section 20: Prevents Infinite Re-teaching Loops)
4. test_multilingual_adaptation (Section 21: Language Switching with State Preservation)
5. test_failure_resilience (Section 34: Graceful Degradation & Health Checks)
6. test_canonical_media_contracts (Section 13, 14, 38: Video, Voice & Avatar endpoints)
"""

import sys
from pathlib import Path
import pytest

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from backend.app.core.models import (
    StudentProfile, LearningRequest, StudentResponse, TeachingStep,
    EvaluationResult, LearningReport
)
from backend.app.services.orchestrator import orchestrator
from backend.app.services.evaluation_engine import evaluation_engine
from backend.app.services.adaptation_engine import adaptation_engine
from backend.app.services.assessment_engine import assessment_engine
from backend.app.services.material_pipeline import material_pipeline
from backend.personalization.service import personalization_service


def test_full_ai_teacher_flow():
    """
    SECTION 32: Complete 22-Step End-to-End Pipeline
    1. Create student
    2. Create learning request
    3. Start lesson
    4. Get TeachingStep
    5. Generate video scene / visual instruction
    6. Generate/mock avatar state
    7. Generate/mock voice narration
    8. Return composed scene
    9. Present question
    10. Submit incorrect response
    11. Evaluate response
    12. Detect misconception
    13. Generate adaptation decision
    14. Generate new TeachingStep
    15. Generate new video scene / visual instruction
    16. Ask follow-up question
    17. Submit correct response
    18. Continue lesson progression
    19. Start summative assessment
    20. Submit assessment answers
    21. Generate LearningReport
    22. Update durable learner profile & verify continuity
    """
    # Step 1: Create student
    student_id = "std_e2e_22step"
    profile = StudentProfile(
        student_id=student_id,
        educational_level="beginner",
        known_topics=["Elementary Math", "Atomic Structure"],
        preferred_language="Hinglish",
        preferred_teaching_style="analogy_driven",
        preferred_depth="intuitive"
    )
    assert profile.student_id == student_id

    # Step 2: Create learning request (Section 6 format)
    request = LearningRequest(
        student_id=student_id,
        topic="Ohm's Law & Circuit Dynamics",
        educational_level="beginner",
        learning_objective="Understand and apply Ohm's law",
        preferred_language="Hinglish",
        teaching_style="analogy_driven",
        available_time=20,
        available_time_minutes=20,
        desired_depth="intuitive"
    )
    assert request.topic == "Ohm's Law & Circuit Dynamics"
    assert request.available_time == 20

    # Step 3: Start lesson (Agent 1 Orchestrator)
    session = orchestrator.create_session(request, profile)
    assert session.session_id is not None
    assert session.status == "teaching"
    assert len(session.steps) >= 3

    # Step 4: Get first TeachingStep
    step1 = orchestrator.get_current_step(session.session_id)
    assert step1 is not None
    assert step1.step_type == "introduction"

    # Step 5: Visual instruction present (not just talking head)
    assert step1.visual_instruction is not None
    assert step1.visual_instruction.type == "circuit"

    # Step 6: Avatar emotional state
    assert step1.avatar_emotion in ["explaining", "attentive", "thoughtful"]

    # Step 7: Voice narration text available
    assert len(step1.explanation) > 20
    assert "ohm" in step1.explanation.lower() or "namaste" in step1.explanation.lower()

    # Step 8: Lesson progression to worked demonstration
    step2, status = orchestrator.advance_step(session.session_id)
    assert step2.step_type == "demonstration"
    assert "V = I * R" in step2.explanation or "V = I" in step2.explanation

    # Step 9: Advance to question step
    step3, status = orchestrator.advance_step(session.session_id)
    assert step3.step_type == "question"
    assert step3.question is not None
    question_id = step3.question.question_id

    # Step 10: Submit incorrect response ("Current increases")
    incorrect_response = StudentResponse(
        session_id=session.session_id,
        question_id=question_id,
        student_answer="Current increase hoga."
    )

    # Step 11 & 12: Evaluate response and detect misconception (Agent 6)
    eval_result = orchestrator.handle_student_response(incorrect_response)
    assert eval_result["adaptation_occurred"] is True
    assert eval_result["evaluation"].correctness is False
    assert "Proportionality" in eval_result["misconception_detected"]

    # Step 13 & 14: Adaptation decision & New TeachingStep synthesized (Agent 1 + Agent 6)
    adapted_step = orchestrator.get_current_step(session.session_id)
    assert adapted_step.step_type == "re_explanation"
    assert adapted_step.step_id != step3.step_id

    # Step 15: Different strategy used (Hydraulic Water Pipe Analogy)
    assert "pipe" in adapted_step.explanation.lower() or "paani" in adapted_step.explanation.lower()
    # Updated visual showing constricted valve (12Ω)
    assert adapted_step.visual_instruction.data["resistance"] == 12.0
    assert adapted_step.visual_instruction.data["current"] == 1.0

    # Step 16: Targeted follow-up question presented
    assert adapted_step.question is not None
    assert adapted_step.question.question_type == "follow_up"

    # Step 17: Submit correct response to follow-up
    correct_response = StudentResponse(
        session_id=session.session_id,
        question_id=adapted_step.question.question_id,
        student_answer="Current kam hokar 1A ho jayega."
    )
    followup_eval = orchestrator.handle_student_response(correct_response)

    # Step 18: System recognizes resolution and advances
    assert followup_eval["evaluation"].correctness is True
    assert followup_eval["adaptation_occurred"] is False

    # Step 19: Start summative assessment (Agent 7)
    assessment_questions = orchestrator.start_assessment(session.session_id)
    assert len(assessment_questions) >= 2
    assert session.status == "assessment"

    # Step 20 & 21: Submit assessment answers & compile LearningReport
    answers = {
        "ohm_assess_1": "V = I * R",
        "ohm_assess_2": "4 Amperes",
        "ohm_assess_3": "Resistance badhta hai"
    }
    report = orchestrator.complete_assessment(session.session_id, answers)
    assert report is not None
    assert report.score >= 80.0
    assert len(report.concepts_understood) > 0
    assert len(report.misconceptions) > 0  # Previously diagnosed and overcome
    assert "Kirchhoff" in report.recommended_next_topic

    # Step 22: Update durable learner profile & verify continuity (Agent 3)
    updated_profile = personalization_service.get_profile(student_id)
    assert updated_profile is not None
    assert updated_profile.student_id == student_id


def test_golden_path_ohms_law():
    """
    SECTION 33: Canonical Golden Path Acceptance Scenario
    Ohm's Law | Beginner | Hinglish | 20 Minutes
    """
    req = LearningRequest(
        student_id="demo_student_01",
        topic="Ohm's Law & Circuit Dynamics",
        educational_level="beginner",
        preferred_language="Hinglish",
        teaching_style="analogy_driven",
        available_time=20
    )
    session = orchestrator.create_session(req)

    # Advance to question
    orchestrator.advance_step(session.session_id)
    orchestrator.advance_step(session.session_id)

    q_step = orchestrator.get_current_step(session.session_id)
    assert q_step.step_type == "question"

    # Intentional wrong answer: "Current increases"
    res = orchestrator.handle_student_response(StudentResponse(
        session_id=session.session_id,
        question_id=q_step.question.question_id,
        student_answer="Current increases"
    ))
    assert res["adaptation_occurred"] is True
    assert "Proportionality" in res["misconception_detected"]

    # Reteach scene must NOT duplicate formula explanation, must use analogy
    reteach_step = orchestrator.get_current_step(session.session_id)
    assert reteach_step.step_type == "re_explanation"
    assert "pipe" in reteach_step.explanation.lower() or "valve" in reteach_step.explanation.lower()

    # Correct follow-up
    res_correct = orchestrator.handle_student_response(StudentResponse(
        session_id=session.session_id,
        question_id=reteach_step.question.question_id,
        student_answer="Current decreases because resistance opposes flow"
    ))
    assert res_correct["evaluation"].correctness is True

    # Complete lesson report
    report = orchestrator.complete_assessment(session.session_id)
    assert report.score >= 85.0
    assert any("inverse" in w.lower() for w in report.weak_areas)


def test_loop_protection():
    """
    SECTION 20: Loop Protection
    Prevents infinite cycles of re-explain -> question -> wrong -> re-explain.
    Max attempts is 2. After exceeding, triggers scaffolded resolution.
    """
    req = LearningRequest(
        student_id="std_loop_test",
        topic="Ohm's Law & Circuit Dynamics",
        preferred_language="English"
    )
    session = orchestrator.create_session(req)

    # Advance to question step
    orchestrator.advance_step(session.session_id)
    orchestrator.advance_step(session.session_id)
    q_step = orchestrator.get_current_step(session.session_id)

    # Attempt 1: Wrong answer -> Adaptation 1
    res1 = orchestrator.handle_student_response(StudentResponse(
        session_id=session.session_id,
        question_id=q_step.question.question_id,
        student_answer="Current increases"
    ))
    assert res1["loop_protection_triggered"] is False
    assert res1["adaptation_occurred"] is True

    # Attempt 2: Wrong answer again on adaptive step
    adapt_step = orchestrator.get_current_step(session.session_id)
    res2 = orchestrator.handle_student_response(StudentResponse(
        session_id=session.session_id,
        question_id=adapt_step.question.question_id,
        student_answer="It increases again"
    ))
    assert res2["loop_protection_triggered"] is False

    # Attempt 3: Exceeds MAX_RETEACH_ATTEMPTS (2) -> Loop Protection fires!
    adapt_step_2 = orchestrator.get_current_step(session.session_id)
    res3 = orchestrator.handle_student_response(StudentResponse(
        session_id=session.session_id,
        question_id=adapt_step_2.question.question_id,
        student_answer="Still increases"
    ))
    assert res3["loop_protection_triggered"] is True
    assert res3["next_step"].step_type == "summary"


def test_multilingual_adaptation():
    """
    SECTION 21: Dynamic Multilingual Adaptation
    Student switches language mid-lesson from English to Hinglish.
    Verifies topic, concept, position, and learner state are strictly preserved.
    """
    req = LearningRequest(
        student_id="std_multilingual",
        topic="Ohm's Law & Circuit Dynamics",
        preferred_language="English"
    )
    session = orchestrator.create_session(req)
    step1 = orchestrator.get_current_step(session.session_id)
    assert step1.language == "English"

    # Switch language to Hinglish
    updated_session = orchestrator.set_session_language(session.session_id, "Hinglish")
    assert updated_session.learning_request.preferred_language == "Hinglish"
    
    # Check that remaining steps now use Hinglish
    current_step = orchestrator.get_current_step(session.session_id)
    assert current_step.language == "Hinglish"
    assert current_step.concept_id == step1.concept_id


def test_failure_resilience():
    """
    SECTION 34: System Failure & Fallback Tests
    1. Unindexed document retrieval returns empty list gracefully.
    2. Unknown session returns None.
    3. Blank student response evaluated without unhandled exceptions.
    """
    # 1. Non-existent document
    chunks = material_pipeline.retrieve("non_existent_doc_id", "Ohm's law")
    assert chunks == []

    # 2. Unknown session
    session = orchestrator.get_session("unknown_sess_xyz")
    assert session is None

    # 3. Empty student response evaluation
    req = LearningRequest(student_id="std_blank", topic="Ohm's Law")
    sess = orchestrator.create_session(req)
    orchestrator.advance_step(sess.session_id)
    orchestrator.advance_step(sess.session_id)
    step = orchestrator.get_current_step(sess.session_id)

    eval_result = evaluation_engine.evaluate(
        response=StudentResponse(
            session_id=sess.session_id,
            question_id=step.question.question_id,
            student_answer=""
        ),
        current_step=step
    )
    assert eval_result is not None
    assert eval_result.correctness is False


def test_http_api_endpoints():
    """
    SECTION 38 & 26: REST API Endpoint Integration
    Verifies /health, /demo/canonical, /sessions/create, /video/generate,
    /voice/generate, and /avatar/generate over HTTP.
    """
    from fastapi.testclient import TestClient
    from backend.app.main import app

    client = TestClient(app)

    # 1. Health check
    res_health = client.get("/health")
    assert res_health.status_code == 200
    data_health = res_health.json()
    assert data_health["status"] == "ok"
    assert data_health["subsystems"]["orchestrator"] == "active"

    # 2. Canonical demo
    res_demo = client.get("/api/demo/canonical")
    assert res_demo.status_code == 200
    data_demo = res_demo.json()
    assert data_demo["status"] == "success"
    assert "Ohm" in data_demo["session"]["learning_request"]["topic"]

    # 3. Create session (flat payload compatibility)
    res_create = client.post("/api/sessions/create", json={
        "student_id": "http_std_01",
        "topic": "Binary Search Algorithm",
        "educational_level": "intermediate",
        "preferred_language": "English",
        "available_time": 15
    })
    assert res_create.status_code == 200
    sess = res_create.json()["session"]
    sess_id = sess["session_id"]

    # 4. Advance step
    res_adv = client.post(f"/api/sessions/{sess_id}/advance")
    assert res_adv.status_code == 200

    # 5. Multilingual switch
    res_lang = client.post(f"/api/sessions/{sess_id}/language", json={"language": "Hinglish"})
    assert res_lang.status_code == 200
    assert res_lang.json()["new_language"] == "Hinglish"

    # 6. Video generation endpoint (Agent 4)
    res_video = client.post("/api/video/generate", json={
        "step_id": "step_01",
        "spoken_text": "Ohm's law explains how current relates to voltage and resistance.",
        "visual_type": "circuit"
    })
    assert res_video.status_code == 200
    assert res_video.json()["status"] == "success"

    # 7. Voice generation endpoint (Agent 5)
    res_voice = client.post("/api/voice/generate", json={
        "text": "Voltage is electrical pressure.",
        "language": "English"
    })
    assert res_voice.status_code == 200
    assert res_voice.json()["status"] == "success"

    # 8. Avatar generation endpoint (Agent 5)
    res_avatar = client.post("/api/avatar/generate", json={"emotion": "explaining"})
    assert res_avatar.status_code == 200
    assert res_avatar.json()["status"] == "success"

