"""
Comprehensive Automated Test Suite for Personalization Engine & Learner Model (Part 3)
Verifies:
- All 15 MANDATORY test cases from Section 41
- REST API endpoints from Section 38
- Integration between Agent 3, Agent 1, Agent 6, Agent 7, and Agent 8
"""

import sys
import threading
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from backend.app.main import app
from backend.personalization.schemas import (
    StudentProfile, StudentPreferences, LearnerKnowledge,
    LearnerEvidence, MisconceptionRecord, LearningHistoryEntry,
    AssessmentHistoryEntry, CreateProfileRequest, UpdateProfileRequest,
    KnowledgeUpdateEvidence, ResetProfileRequest
)
from backend.personalization.service import PersonalizationService
from backend.personalization.repository import SQLiteProfileRepository, InMemoryProfileRepository
from backend.personalization.mastery_model import MasteryModel
from backend.personalization.engine import PersonalizationEngine

# Use dedicated test DB to isolate test state
TEST_DB_PATH = Path(__file__).resolve().parent / "test_learner_profiles.db"

@pytest.fixture(autouse=True)
def setup_teardown_test_env():
    import sqlite3
    if TEST_DB_PATH.exists():
        try:
            TEST_DB_PATH.unlink()
        except Exception:
            try:
                conn = sqlite3.connect(TEST_DB_PATH)
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [r[0] for r in cursor.fetchall() if not r[0].startswith("sqlite_")]
                for t in tables:
                    cursor.execute(f"DELETE FROM {t}")
                conn.commit()
                conn.close()
            except Exception:
                pass
    yield
    if TEST_DB_PATH.exists():
        try:
            TEST_DB_PATH.unlink()
        except Exception:
            pass

@pytest.fixture
def test_service():
    repo = SQLiteProfileRepository(db_path=TEST_DB_PATH)
    return PersonalizationService(repository=repo)

# ----------------- 15 MANDATORY TESTS (Section 41) -----------------

def test_1_create_new_student(test_service):
    """TEST 1: Create new student -> Expected: valid profile."""
    req = CreateProfileRequest(
        student_id="student_001",
        educational_level="beginner",
        preferred_language="English",
        preferred_teaching_style="analogy_based",
        preferred_depth="standard"
    )
    profile = test_service.create_or_update_profile(req)
    assert profile.student_id == "student_001"
    assert profile.educational_level == "beginner"
    assert profile.preferred_language == "English"
    assert profile.preferences.preferred_teaching_style == "analogy_based"
    assert profile.concept_mastery == {}
    assert profile.learning_history == []

def test_2_update_language(test_service):
    """TEST 2: Update language -> Expected: only language changes."""
    req = CreateProfileRequest(
        student_id="student_002",
        educational_level="intermediate",
        preferred_language="English",
        preferred_teaching_style="technical",
        preferred_depth="deep"
    )
    test_service.create_or_update_profile(req)

    # Patch only language
    patch_req = UpdateProfileRequest(preferred_language="Hindi")
    updated = test_service.update_profile("student_002", patch_req)

    assert updated.preferred_language == "Hindi"
    assert updated.preferences.preferred_language == "Hindi"
    # Other preferences remain untouched
    assert updated.educational_level == "intermediate"
    assert updated.preferences.preferred_teaching_style == "technical"
    assert updated.preferences.preferred_depth == "deep"

def test_3_existing_profile_current_request_override(test_service):
    """TEST 3: Existing profile (English) + current request override (Hindi) -> Expected: Hindi."""
    req = CreateProfileRequest(
        student_id="student_003",
        preferred_language="English",
        educational_level="beginner"
    )
    test_service.create_or_update_profile(req)

    class CurrentSessionRequest:
        preferred_language = "Hindi"
        educational_level = None
        topic = "Ohm's Law"

    ctx = test_service.get_personalization_context("student_003", topic="Ohm's Law", request=CurrentSessionRequest())
    assert ctx.preferred_language == "Hindi"
    assert any("Hindi" in r for r in ctx.reasoning)

def test_4_beginner_profile_constraints(test_service):
    """TEST 4: Beginner profile -> Expected: beginner personalization constraints."""
    req = CreateProfileRequest(
        student_id="student_004",
        educational_level="beginner"
    )
    test_service.create_or_update_profile(req)

    ctx = test_service.get_personalization_context("student_004", topic="Circuits")
    assert ctx.learner_level == "beginner"
    # Check actionable constraints
    assert any("Define all domain-specific terminology" in c for c in ctx.explanation_constraints)
    assert any("everyday real-world analogies" in c for c in ctx.explanation_constraints)
    assert any("Avoid heavy mathematical formalisms" in c for c in ctx.explanation_constraints)
    assert any("conceptual checks before any numerical tasks" in c for c in ctx.question_constraints)

def test_5_advanced_profile_constraints(test_service):
    """TEST 5: Advanced profile -> Expected: advanced personalization constraints."""
    req = CreateProfileRequest(
        student_id="student_005",
        educational_level="advanced"
    )
    test_service.create_or_update_profile(req)

    ctx = test_service.get_personalization_context("student_005", topic="Circuits")
    assert ctx.learner_level == "advanced"
    assert any("rigorous mathematical formulation" in c for c in ctx.explanation_constraints)
    assert any("edge cases" in c for c in ctx.explanation_constraints)
    assert any("multi-step problems" in c for c in ctx.question_constraints)

def test_6_record_correct_answer_mastery_increase(test_service):
    """TEST 6: Record correct answer -> Expected: mastery increases."""
    student_id = "student_006"
    test_service.create_or_update_profile(CreateProfileRequest(student_id=student_id))

    ev1 = LearnerEvidence(
        source="lesson_response",
        question_id="q1",
        score=0.90,
        result="correct"
    )
    k1 = test_service.update_concept_knowledge(student_id, "voltage", ev1)
    assert k1.mastery_score > 0.0
    assert k1.attempts == 1
    assert k1.correct_attempts == 1

    # Second correct attempt
    ev2 = LearnerEvidence(
        source="lesson_response",
        question_id="q2",
        score=0.95,
        result="correct"
    )
    k2 = test_service.update_concept_knowledge(student_id, "voltage", ev2)
    assert k2.mastery_score > k1.mastery_score
    assert k2.confidence > k1.confidence

def test_7_record_incorrect_answer_mastery_decrease(test_service):
    """TEST 7: Record incorrect answer -> Expected: mastery decreases."""
    student_id = "student_007"
    test_service.create_or_update_profile(CreateProfileRequest(student_id=student_id))

    # Start with high score
    test_service.update_concept_knowledge(student_id, "current", LearnerEvidence(
        source="assessment", score=0.85, result="correct"
    ))
    initial_k = test_service.repository.get_knowledge_state(student_id, "current")["current"]
    initial_score = initial_k.mastery_score

    # Student makes an error
    ev_wrong = LearnerEvidence(
        source="lesson_response",
        question_id="q_curr_1",
        score=0.10,
        result="incorrect"
    )
    k_after = test_service.update_concept_knowledge(student_id, "current", ev_wrong)
    assert k_after.mastery_score < initial_score
    assert k_after.incorrect_attempts == 1

def test_8_record_misconception(test_service):
    """TEST 8: Record misconception -> Expected: misconception stored with status 'misconception'."""
    student_id = "student_008"
    test_service.create_or_update_profile(CreateProfileRequest(student_id=student_id))

    ev = LearnerEvidence(
        source="lesson_response",
        question_id="q_ohm",
        score=0.15,
        result="misconception",
        misconception="Current increases when resistance increases"
    )
    k = test_service.update_concept_knowledge(student_id, "resistance", ev)
    assert k.status == "misconception"
    assert len(k.misconceptions) == 1
    assert k.misconceptions[0].misconception == "Current increases when resistance increases"
    assert k.misconceptions[0].occurrences == 1
    assert k.misconceptions[0].resolved is False

def test_9_successful_retest_resolves_misconception(test_service):
    """TEST 9: Successful re-test -> Expected: mastery improves and misconception resolved."""
    student_id = "student_009"
    test_service.create_or_update_profile(CreateProfileRequest(student_id=student_id))

    # Step A: Misconception
    ev_misc = LearnerEvidence(
        source="lesson_response",
        question_id="q_ohm_1",
        score=0.1,
        result="misconception",
        misconception="Resistance increases current"
    )
    k_bad = test_service.update_concept_knowledge(student_id, "resistance", ev_misc)
    assert k_bad.status == "misconception"
    assert k_bad.misconceptions[0].resolved is False

    # Step B: Successful re-test after teacher's hydraulic analogy intervention
    ev_retest = LearnerEvidence(
        source="lesson_response",
        question_id="q_ohm_retest",
        score=0.95,
        result="correct"
    )
    k_good = test_service.update_concept_knowledge(student_id, "resistance", ev_retest)
    assert k_good.mastery_score > k_bad.mastery_score
    assert k_good.misconceptions[0].resolved is True
    assert k_good.status != "misconception"

def test_10_assessment_update(test_service):
    """TEST 10: Assessment update -> Expected: concept scores update learner knowledge."""
    student_id = "student_010"
    test_service.create_or_update_profile(CreateProfileRequest(student_id=student_id))

    entry = AssessmentHistoryEntry(
        assessment_id="ass_101",
        lesson_id="les_01",
        topic="Ohm's Law",
        score=0.82,
        concept_scores={
            "voltage": 0.90,
            "current": 0.85,
            "resistance": 0.55
        },
        weak_concepts=["resistance"],
        strong_concepts=["voltage", "current"],
        misconceptions=[]
    )
    recorded = test_service.record_assessment_result(student_id, entry)
    assert recorded.score == 0.82

    # Check that concept_mastery table was updated for each tested concept
    knowledge = test_service.repository.get_knowledge_state(student_id)
    assert "voltage" in knowledge
    assert "current" in knowledge
    assert "resistance" in knowledge
    assert knowledge["voltage"].mastery_score >= 0.80
    assert knowledge["resistance"].mastery_score < 0.70

def test_11_topic_specific_context(test_service):
    """TEST 11: Topic-specific context -> Expected: only relevant concepts returned."""
    student_id = "student_011"
    test_service.create_or_update_profile(CreateProfileRequest(student_id=student_id))

    # Populate multiple concepts across domains
    test_service.update_concept_knowledge(student_id, "voltage", LearnerEvidence(source="assessment", score=0.90, result="correct"))
    test_service.update_concept_knowledge(student_id, "current", LearnerEvidence(source="assessment", score=0.75, result="correct"))
    test_service.update_concept_knowledge(student_id, "linear_algebra", LearnerEvidence(source="assessment", score=0.80, result="correct"))

    # Request Ohm's Law context: should include voltage and current, but exclude linear_algebra
    ctx = test_service.get_personalization_context(student_id, topic="Ohm's Law")
    assert "voltage" in ctx.topic_mastery
    assert "current" in ctx.topic_mastery
    assert "linear_algebra" not in ctx.topic_mastery

def test_12_historical_profile(test_service):
    """TEST 12: Historical profile -> Expected: learning history retained."""
    student_id = "student_012"
    test_service.create_or_update_profile(CreateProfileRequest(student_id=student_id))

    entry1 = LearningHistoryEntry(
        session_id="ses_1",
        lesson_id="les_1",
        topic="Electric Charge",
        duration_minutes=15.0,
        concepts_covered=["charge", "atoms"],
        concepts_mastered=["charge"],
        assessment_score=0.88
    )
    entry2 = LearningHistoryEntry(
        session_id="ses_2",
        lesson_id="les_2",
        topic="Voltage & Potential",
        duration_minutes=20.0,
        concepts_covered=["voltage", "potential"],
        concepts_mastered=["voltage"],
        assessment_score=0.92
    )
    test_service.record_learning_session(student_id, entry1)
    test_service.record_learning_session(student_id, entry2)

    hist = test_service.get_recent_learning_history(student_id, limit=5)
    assert len(hist) == 2
    assert hist[0].topic == "Voltage & Potential"  # Descending order
    assert hist[1].topic == "Electric Charge"

def test_13_current_session_time_override(test_service):
    """TEST 13: Current-session time (Profile: 60 min, Request: 5 min) -> Expected: context = 5 min."""
    student_id = "student_013"
    req = CreateProfileRequest(
        student_id=student_id,
        preferences={"typical_duration": 60}
    )
    test_service.create_or_update_profile(req)

    class QuickRequest:
        available_time_minutes = 5.0
        educational_level = None
        preferred_language = None
        teaching_style = None
        desired_depth = None
        topic = "Capacitance"

    ctx = test_service.get_personalization_context(student_id, request=QuickRequest())
    assert ctx.available_time_minutes == 5.0
    assert any("Time is constrained" in c for c in ctx.explanation_constraints)

def test_14_explicit_preference_priority(test_service):
    """TEST 14: Explicit preference priority (Profile: advanced, Current request: beginner) -> Expected: beginner."""
    student_id = "student_014"
    req = CreateProfileRequest(
        student_id=student_id,
        educational_level="advanced"
    )
    test_service.create_or_update_profile(req)

    class BeginnerOverrideRequest:
        educational_level = "beginner"
        preferred_language = None
        teaching_style = None
        desired_depth = None
        available_time_minutes = 20.0
        topic = "Quantum Basics"

    ctx = test_service.get_personalization_context(student_id, request=BeginnerOverrideRequest())
    assert ctx.learner_level == "beginner"
    assert any("Define all domain-specific terminology" in c for c in ctx.explanation_constraints)

def test_15_concurrent_updates(test_service):
    """TEST 15: Concurrent updates -> Expected: no accidental loss of mastery evidence."""
    student_id = "student_015"
    test_service.create_or_update_profile(CreateProfileRequest(student_id=student_id))

    def worker(concept: str, score: float):
        ev = LearnerEvidence(
            source="lesson_response",
            result="correct" if score >= 0.7 else "incorrect",
            score=score
        )
        test_service.update_concept_knowledge(student_id, concept, ev)

    threads = []
    concepts = ["concept_a", "concept_b", "concept_c", "concept_d", "concept_e"]
    for c in concepts:
        t = threading.Thread(target=worker, args=(c, 0.85))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    knowledge_map = test_service.repository.get_knowledge_state(student_id)
    assert len(knowledge_map) == 5
    for c in concepts:
        assert c in knowledge_map
        assert knowledge_map[c].attempts == 1
        assert knowledge_map[c].correct_attempts == 1


# ----------------- REST API TESTS (Section 38 & Endpoints) -----------------

def test_api_profile_lifecycle():
    client = TestClient(app)
    stu_id = "api_stu_99"

    # 1. Create profile
    res_create = client.post("/api/students/profile", json={
        "student_id": stu_id,
        "educational_level": "beginner",
        "preferred_language": "Hinglish",
        "preferred_teaching_style": "analogy_based"
    })
    assert res_create.status_code == 200
    data = res_create.json()
    assert data["student_id"] == stu_id
    assert data["preferred_language"] == "Hinglish"

    # 2. Get profile
    res_get = client.get(f"/api/students/{stu_id}/profile")
    assert res_get.status_code == 200
    assert res_get.json()["student_id"] == stu_id

    # 3. Patch profile
    res_patch = client.patch(f"/api/students/{stu_id}/profile", json={
        "preferred_language": "Hindi"
    })
    assert res_patch.status_code == 200
    assert res_patch.json()["preferred_language"] == "Hindi"

    # 4. Ingest knowledge evidence
    res_ev = client.post(f"/api/students/{stu_id}/knowledge/update?concept_id=resistance", json={
        "source": "lesson_response",
        "correctness": 0.15,
        "classification": "misconception",
        "misconception": "Current increases with resistance",
        "confidence": 0.95
    })
    assert res_ev.status_code == 200
    assert res_ev.json()["status"] == "misconception"

    # 5. Get compact learning context
    res_ctx = client.get(f"/api/students/{stu_id}/learning-context?topic=Ohm's Law")
    assert res_ctx.status_code == 200
    ctx_data = res_ctx.json()
    assert ctx_data["student_id"] == stu_id
    assert len(ctx_data["explanation_constraints"]) > 0
    assert len(ctx_data["misconceptions"]) > 0

    # 6. Reset knowledge
    res_reset = client.post(f"/api/students/{stu_id}/reset", json={
        "reset_type": "RESET_KNOWLEDGE"
    })
    assert res_reset.status_code == 200
    # Verify knowledge cleared but profile exists
    res_after_reset = client.get(f"/api/students/{stu_id}/profile")
    assert res_after_reset.status_code == 200
    assert len(res_after_reset.json()["concept_mastery"]) == 0

def test_orchestrator_integration_with_personalization():
    """Verifies that Agent 1 Orchestrator seamlessly accesses Agent 3 Personalization."""
    from backend.teaching.providers.profile_provider import student_profile_provider
    from backend.personalization.service import personalization_service
    from backend.personalization.schemas import CreateProfileRequest, LearnerEvidence

    stu_id = "orch_stu_01"
    personalization_service.create_or_update_profile(CreateProfileRequest(
        student_id=stu_id,
        educational_level="beginner",
        preferred_language="Hinglish",
        preferred_teaching_style="analogy_based"
    ))

    # Add prior struggle in resistance
    personalization_service.update_concept_knowledge(stu_id, "resistance", LearnerEvidence(
        source="lesson_response",
        result="misconception",
        score=0.15,
        misconception="Current increases with resistance"
    ))

    # 1. ProfileProvider retrieves from Agent 3
    retrieved_dict = student_profile_provider.get_student_profile(stu_id)
    assert retrieved_dict["student_id"] == stu_id
    assert retrieved_dict["preferred_language"] == "Hinglish"
    assert "resistance" in retrieved_dict["weak_concepts"]

    # 2. Teaching Brain gets compact context
    context = personalization_service.get_personalization_context(stu_id, topic="Ohm's Law")
    assert context.preferred_language == "Hinglish"
    assert "resistance" in context.weak_concepts
    assert any("resistance" in m.lower() for m in context.misconceptions)
    assert any("Define all domain-specific terminology" in c for c in context.explanation_constraints)
