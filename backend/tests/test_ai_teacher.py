"""
Unit tests for AI Teacher Subsystem:
1. Data Contracts validation (Section 6)
2. Lesson Planning & Prerequisites
3. Misconception Evaluation
4. Dynamic Pedagogical Adaptation (Step Injection)
5. Summative Assessment & LearningReport compilation
"""

import sys
from pathlib import Path
import pytest

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from backend.app.core.models import (
    StudentProfile, LearningRequest, StudentResponse
)
from backend.app.services.orchestrator import orchestrator
from backend.app.services.evaluation_engine import evaluation_engine
from backend.app.services.adaptation_engine import adaptation_engine

def test_data_contracts_and_session_creation():
    request = LearningRequest(
        student_id="std_101",
        topic="Ohm's Law & Circuit Dynamics",
        educational_level="beginner",
        preferred_language="Hinglish",
        available_time=20
    )
    profile = StudentProfile(
        student_id="std_101",
        educational_level="beginner",
        preferred_language="Hinglish"
    )

    session = orchestrator.create_session(request, profile)
    assert session.session_id is not None
    assert session.lesson_plan is not None
    assert session.lesson_plan.topic == "Ohm's Law & Circuit Dynamics"
    assert len(session.lesson_plan.prerequisites) > 0
    assert len(session.lesson_plan.ordered_concepts) > 0
    assert len(session.steps) >= 3

def test_step_progression_and_questioning():
    request = LearningRequest(
        student_id="std_102",
        topic="Ohm's Law & Circuit Dynamics",
        preferred_language="Hinglish"
    )
    session = orchestrator.create_session(request)
    
    # First step: intro
    step1 = orchestrator.get_current_step(session.session_id)
    assert step1.step_type == "introduction"
    assert step1.visual_instruction is not None
    assert step1.visual_instruction.type == "circuit"

    # Advance to step 2: demonstration
    step2, status = orchestrator.advance_step(session.session_id)
    assert step2.step_type == "demonstration"

    # Advance to step 3: diagnostic question
    step3, status = orchestrator.advance_step(session.session_id)
    assert step3.step_type == "question"
    assert step3.question is not None
    assert "constant" in step3.question.prompt.lower()

def test_misconception_detection_and_adaptive_intervention():
    """
    CRITICAL TEST:
    Canonical Demo Scenario:
    Teacher asks what happens to current if resistance increases while voltage is constant.
    Student answers: 'Current increases'.
    The system MUST:
    1. Recognize 'Inverted Proportionality' misconception.
    2. Recommend 'give_analogy'.
    3. Insert adaptive re-explanation step right after the current step.
    4. Provide the hydraulic water pipe analogy and follow-up question.
    """
    request = LearningRequest(
        student_id="std_103",
        topic="Ohm's Law & Circuit Dynamics",
        preferred_language="Hinglish"
    )
    session = orchestrator.create_session(request)
    
    # Move to question step
    orchestrator.advance_step(session.session_id)
    orchestrator.advance_step(session.session_id)
    
    current_step = orchestrator.get_current_step(session.session_id)
    assert current_step.step_type == "question"

    # Student gives wrong answer: "Current increases"
    response = StudentResponse(
        session_id=session.session_id,
        question_id=current_step.question.question_id,
        student_answer="Current increases"
    )

    eval_result = orchestrator.handle_student_response(response)
    assert eval_result["adaptation_occurred"] is True
    assert "Proportionality" in eval_result["misconception_detected"]
    
    # Check that current active step is now the adaptive re-explanation
    adaptive_step = orchestrator.get_current_step(session.session_id)
    assert adaptive_step.step_type == "re_explanation"
    assert "pipe" in adaptive_step.explanation.lower() or "paani" in adaptive_step.explanation.lower()
    assert adaptive_step.question is not None

def test_correct_followup_and_learning_report():
    """
    Following the adaptation, student gives the correct answer to the follow-up question.
    The system confirms resolution and advances.
    """
    request = LearningRequest(
        student_id="std_104",
        topic="Ohm's Law & Circuit Dynamics",
        preferred_language="English"
    )
    session = orchestrator.create_session(request)
    orchestrator.advance_step(session.session_id)
    orchestrator.advance_step(session.session_id)

    # 1. Wrong answer
    orchestrator.handle_student_response(StudentResponse(
        session_id=session.session_id,
        question_id="ohm_q1",
        student_answer="Current increases"
    ))

    # 2. Adaptive step is active, student answers follow-up correctly: "Current decreases to 1A"
    adaptive_step = orchestrator.get_current_step(session.session_id)
    followup_resp = StudentResponse(
        session_id=session.session_id,
        question_id=adaptive_step.question.question_id,
        student_answer="Current decreases to 1A because resistance opposes flow"
    )
    res = orchestrator.handle_student_response(followup_resp)
    assert res["adaptation_occurred"] is False
    assert res["evaluation"].correctness is True

    # Complete assessment
    report = orchestrator.complete_assessment(session.session_id)
    assert report.score > 80.0
    assert len(report.misconceptions) > 0
    assert "Kirchhoff" in report.recommended_next_topic
