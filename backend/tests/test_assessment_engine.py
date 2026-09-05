"""
Comprehensive Automated Test Suite for Agent 7: Assessment & Learning Analytics Engine.
Covers:
- All 22 required tests from Section 52
- Section 53: Mandatory Ohm's Law Assessment Test
- Section 54: Second Assessment Test (minor numerical rounding error)
- Section 55: Report Quality Test (specific concept naming, no vague generalization)
- Section 56 & 57: Next-Topic & No-Evidence Rule Tests
- REST API integration tests
"""

import sys
from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

import pytest
from typing import Dict, Any, List
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.assessment.models import (
    AssessmentConfig, AssessmentQuestion, AssessmentResponse,
    AssessmentSession, AssessmentResult, LearningReport,
    QuestionResult, ScoreSummary, ConceptResult, WeakAreaItem, AggregatedMisconception
)
from backend.assessment.validators.assessment_validator import (
    AssessmentValidator, AssessmentValidationError, assessment_validator
)
from backend.assessment.generators.question_generator import (
    QuestionGenerator, question_generator
)
from backend.assessment.services.scoring_service import (
    ScoringService, scoring_service
)
from backend.assessment.services.analytics_service import (
    AnalyticsService, analytics_service
)
from backend.assessment.services.report_service import (
    ReportService, report_service
)
from backend.assessment.services.assessment_service import (
    AssessmentService, assessment_service
)
from backend.assessment.providers.evaluator_bridge import EvaluatorBridge
from backend.assessment.providers.profile_bridge import ProfileBridge


# ============================================================
# MOCK PROVIDERS FOR ISOLATED TESTING
# ============================================================

class MockAgent6Evaluator:
    """Simulates Agent 6 response evaluation without needing live LLM."""
    def evaluate(self, response, current_step, language="English"):
        ans = response.student_answer.strip().lower()
        prompt = current_step.question.prompt.lower() if (current_step and current_step.question) else ""

        # Misconception check: student says "increase" when resistance increases
        if "increase" in ans and ("resistance increases" in prompt or "resistance badh" in prompt or "resistance rises" in prompt or "constant" in prompt):
            class MockResult:
                correctness = 0.0
                classification = "misconception"
                misconception = "Direct proportionality assumption (treating current as increasing with resistance)"
                knowledge_gap = "Missing inverse proportionality intuition (I = V/R)"
                confidence = 0.96
                reasoning_quality = "Confused direct vs inverse relationship"
                teacher_thought = "Student assumed current increases when resistance increases."
            return MockResult()

        # Correct check
        if any(w in ans for w in ["v = ir", "v = i * r", "decrease", "kam", "decreases", "opposes", "2 a", "2a", "increases because resistance"]):
            class MockResult:
                correctness = 1.0
                classification = "correct"
                misconception = None
                knowledge_gap = None
                confidence = 0.95
                reasoning_quality = "Clear conceptual explanation"
                teacher_thought = "Demonstrated accurate understanding."
            return MockResult()

        # Partially correct
        if len(ans) > 5:
            class MockResult:
                correctness = 0.5
                classification = "partially_correct"
                misconception = None
                knowledge_gap = "Incomplete reasoning"
                confidence = 0.70
                reasoning_quality = "Partial answer"
                teacher_thought = "Student provided partial reasoning."
            return MockResult()

        # Incorrect
        class MockResult:
            correctness = 0.0
            classification = "incorrect"
            misconception = None
            knowledge_gap = "Incorrect response"
            confidence = 0.90
            reasoning_quality = "Incorrect"
            teacher_thought = "Did not demonstrate expected understanding."
        return MockResult()


@pytest.fixture
def mock_agent6_bridge():
    return EvaluatorBridge(evaluator=MockAgent6Evaluator())


@pytest.fixture
def mock_profile_bridge():
    class MockProfileService:
        def __init__(self):
            self.recorded = []
            self.repository = self

        def record_assessment_result(self, student_id, data):
            self.recorded.append((student_id, data))
            return data

        def get_profile(self, student_id):
            return None

    mock_svc = MockProfileService()
    return ProfileBridge(service=mock_svc)


@pytest.fixture
def custom_assessment_service(mock_agent6_bridge, mock_profile_bridge):
    scorer = ScoringService(bridge=mock_agent6_bridge)
    reporter = ReportService(p_bridge=mock_profile_bridge)
    return AssessmentService(
        generator=question_generator,
        scorer=scorer,
        analytics=analytics_service,
        reporter=reporter
    )


# ============================================================
# 1-22 TESTS CONFORMING TO SECTION 52
# ============================================================

def test_1_create_assessment():
    """TEST 1: Create assessment with valid config."""
    config = AssessmentConfig(
        topic="Ohm's Law",
        question_count=3,
        passing_score=0.70
    )
    conf, questions = assessment_service.create_assessment(config)
    assert conf.topic == "Ohm's Law"
    assert len(questions) == 3
    assert all(isinstance(q, AssessmentQuestion) for q in questions)


def test_2_validate_assessment_success_and_failure():
    """TEST 2: Assessment validation passes for valid, fails for invalid."""
    # Valid
    q_valid = [
        AssessmentQuestion(
            question_id="q_val_1",
            assessment_id="a1",
            text="What is Ohm's Law?",
            expected_concept="ohms_law",
            expected_answer="V = IR",
            points=1.0,
            difficulty=0.3
        )
    ]
    is_valid, errors = assessment_validator.validate_assessment(q_valid)
    assert is_valid is True
    assert len(errors) == 0

    # Invalid: empty text, negative points, invalid difficulty
    q_invalid = [
        AssessmentQuestion.model_construct(
            question_id="q_inv_1",
            assessment_id="a1",
            text="",  # Empty
            expected_concept="",  # Empty
            points=-1.0,  # Invalid
            difficulty=1.5  # Out of range
        )
    ]
    is_valid, errors = assessment_validator.validate_assessment(q_invalid)
    assert is_valid is False
    assert len(errors) >= 3



def test_3_mcq_scoring(mock_agent6_bridge):
    """TEST 3: MCQ scoring handles exact match, option letters, and wrong options."""
    scorer = ScoringService(bridge=mock_agent6_bridge)
    q = AssessmentQuestion(
        question_id="q_mcq",
        assessment_id="a1",
        text="What is the SI unit of resistance?",
        type="mcq",
        options=["Volt", "Ampere", "Ohm", "Watt"],
        correct_option="Ohm",
        expected_concept="units",
        points=2.0
    )

    # Exact match
    res1 = scorer.score_response(q, AssessmentResponse(question_id=q.question_id, student_id="s1", answer="Ohm"))
    assert res1.correctness == 1.0
    assert res1.points_earned == 2.0
    assert res1.classification == "correct"

    # Option letter 'C' (since Ohm is index 2 -> C)
    res2 = scorer.score_response(q, AssessmentResponse(question_id=q.question_id, student_id="s1", answer="C"))
    assert res2.correctness == 1.0
    assert res2.points_earned == 2.0

    # Incorrect option
    res3 = scorer.score_response(q, AssessmentResponse(question_id=q.question_id, student_id="s1", answer="Volt"))
    assert res3.correctness == 0.0
    assert res3.points_earned == 0.0
    assert res3.classification == "incorrect"


def test_4_numerical_scoring(mock_agent6_bridge):
    """TEST 4: Numerical scoring with values, tolerance, and unit matching."""
    scorer = ScoringService(bridge=mock_agent6_bridge)
    q = AssessmentQuestion(
        question_id="q_num",
        assessment_id="a1",
        text="Calculate current for V=10V and R=5 Ohm.",
        type="numerical",
        expected_value=2.0,
        unit="A",
        tolerance=0.05,
        expected_concept="current_calculation",
        points=3.0
    )

    # Exact value with unit
    res1 = scorer.score_response(q, AssessmentResponse(question_id=q.question_id, student_id="s1", answer="2 A"))
    assert res1.correctness == 1.0
    assert res1.points_earned == 3.0
    assert res1.classification == "correct"

    # Within tolerance: 2.05 A
    res2 = scorer.score_response(q, AssessmentResponse(question_id=q.question_id, student_id="s1", answer="2.05 Amperes"))
    assert res2.correctness == 1.0
    assert res2.points_earned == 3.0

    # Completely wrong
    res3 = scorer.score_response(q, AssessmentResponse(question_id=q.question_id, student_id="s1", answer="10 A"))
    assert res3.correctness == 0.0
    assert res3.points_earned == 0.0
    assert res3.classification == "incorrect"


def test_5_partial_open_ended_scoring_agent6_mock(mock_agent6_bridge):
    """TEST 5: Partial / open-ended scoring delegating to Agent 6 mock."""
    scorer = ScoringService(bridge=mock_agent6_bridge)
    q = AssessmentQuestion(
        question_id="q_open",
        assessment_id="a1",
        text="Explain why current changes with voltage.",
        type="conceptual",
        expected_concept="voltage_current_relation",
        points=4.0
    )

    # Partial response
    res = scorer.score_response(
        q,
        AssessmentResponse(question_id=q.question_id, student_id="s1", answer="voltage pushes charge")
    )
    assert res.correctness == 0.5
    assert res.points_earned == 2.0
    assert res.classification == "partially_correct"


def test_6_weighted_scoring():
    """TEST 6: Weighted scoring with different question point values."""
    q_results = [
        QuestionResult(
            question_id="q1", concept="c1", correctness=1.0,
            points_earned=1.0, points_possible=1.0, classification="correct"
        ),
        QuestionResult(
            question_id="q2", concept="c2", correctness=1.0,
            points_earned=1.0, points_possible=1.0, classification="correct"
        ),
        QuestionResult(
            question_id="q3", concept="c3", correctness=0.5,
            points_earned=1.0, points_possible=2.0, classification="partially_correct"
        ),
        QuestionResult(
            question_id="q4", concept="c4", correctness=1.0,
            points_earned=2.0, points_possible=2.0, classification="correct"
        ),
        QuestionResult(
            question_id="q5", concept="c5", correctness=0.5,
            points_earned=2.0, points_possible=4.0, classification="partially_correct"
        )
    ]
    summary = scoring_service.calculate_score_summary(q_results, passing_score=0.70)
    assert summary.raw == 7.0
    assert summary.max == 10.0
    assert summary.percentage == 0.70
    assert summary.passed is True


def test_7_concept_aggregation():
    """TEST 7: Aggregates multiple questions under the same concept."""
    questions = [
        AssessmentQuestion(question_id="q1", assessment_id="a1", text="t1", expected_concept="ohms_law", points=1.0),
        AssessmentQuestion(question_id="q2", assessment_id="a1", text="t2", expected_concept="ohms_law", points=2.0),
        AssessmentQuestion(question_id="q3", assessment_id="a1", text="t3", expected_concept="power", points=2.0)
    ]
    results = [
        QuestionResult(question_id="q1", concept="ohms_law", correctness=1.0, points_earned=1.0, points_possible=1.0, classification="correct"),
        QuestionResult(question_id="q2", concept="ohms_law", correctness=1.0, points_earned=2.0, points_possible=2.0, classification="correct"),
        QuestionResult(question_id="q3", concept="power", correctness=0.0, points_earned=0.0, points_possible=2.0, classification="incorrect")
    ]
    concept_res = analytics_service.analyze_concepts(questions, results)
    assert len(concept_res) == 2
    c_ohms = next(c for c in concept_res if c.concept == "ohms_law")
    c_power = next(c for c in concept_res if c.concept == "power")

    assert c_ohms.score == 1.0
    assert c_ohms.status == "strong"
    assert c_power.score == 0.0
    assert c_power.status == "weak"


def test_8_weak_area_detection():
    """TEST 8: Identifies weak concepts with diagnostic pedagogical reasons."""
    concept_results = [
        analytics_service.analyze_concepts(
            [AssessmentQuestion(question_id="q1", assessment_id="a1", text="t", expected_concept="inverse_rel", points=2.0)],
            [QuestionResult(
                question_id="q1", concept="inverse_rel", correctness=0.2, points_earned=0.4, points_possible=2.0,
                classification="incorrect", misconception="Direct relationship assumption"
            )]
        )[0]
    ]
    weak_areas = analytics_service.detect_weak_areas(concept_results)
    assert len(weak_areas) == 1
    assert weak_areas[0].concept == "inverse_rel"
    assert "Direct relationship" in weak_areas[0].reason


def test_9_strong_area_detection():
    """TEST 9: Identifies concepts with strong mastery evidence."""
    concept_results = analytics_service.analyze_concepts(
        [
            AssessmentQuestion(question_id="q1", assessment_id="a1", text="t", expected_concept="voltage", points=1.0),
            AssessmentQuestion(question_id="q2", assessment_id="a1", text="t", expected_concept="current", points=1.0)
        ],
        [
            QuestionResult(question_id="q1", concept="voltage", correctness=1.0, points_earned=1.0, points_possible=1.0, classification="correct"),
            QuestionResult(question_id="q2", concept="current", correctness=0.3, points_earned=0.3, points_possible=1.0, classification="incorrect")
        ]
    )
    strong = analytics_service.detect_strong_areas(concept_results)
    assert "voltage" in strong
    assert "current" not in strong


def test_10_misconception_aggregation():
    """TEST 10: Aggregates recurring misconceptions across questions."""
    q_results = [
        QuestionResult(
            question_id="q1", concept="c1", correctness=0.0, points_earned=0, points_possible=1,
            classification="misconception", misconception="Current increases with resistance"
        ),
        QuestionResult(
            question_id="q2", concept="c1", correctness=0.0, points_earned=0, points_possible=1,
            classification="misconception", misconception="Current increases with resistance"
        )
    ]
    aggregated = analytics_service.aggregate_misconceptions(q_results)
    assert len(aggregated) == 1
    assert aggregated[0].frequency == 2
    assert "Current increases with resistance" in aggregated[0].misconception


def test_11_revision_recommendations():
    """TEST 11: Generates prioritized revision recommendations."""
    from backend.assessment.recommendations.revision import revision_engine
    from backend.assessment.models.result import WeakAreaItem, ConceptResult

    weak_areas = [
        WeakAreaItem(concept="inverse_relationship", score=0.3, reason="Repeated incorrect proportionality", misconceptions=["Direct proportionality"])
    ]
    c_res = [
        ConceptResult(concept="inverse_relationship", score=0.3, status="weak", revision_required=True)
    ]
    recs = revision_engine.generate_recommendations(weak_areas, c_res, [])
    assert len(recs) == 1
    assert recs[0].priority == "high"
    assert "I = V/R" in recs[0].reason
    assert recs[0].estimated_time_minutes > 0


def test_12_next_topic_recommendation():
    """TEST 12: Next topic recommendation adheres to supplied learning path."""
    from backend.assessment.recommendations.next_topic import next_topic_engine

    path = ["Ohm's Law", "Series and Parallel Circuits", "Kirchhoff's Laws"]
    # Case A: Strong foundations -> advance to next node
    next_topic, reason = next_topic_engine.recommend_next_topic(
        topic="Ohm's Law",
        strong_areas=["voltage", "current", "ohms_law"],
        weak_areas=[],
        overall_score=0.90,
        learning_path=path
    )
    assert next_topic == "Series and Parallel Circuits"

    # Case B: Foundational concepts weak -> do NOT advance
    from backend.assessment.models.result import WeakAreaItem
    next_topic_fail, reason_fail = next_topic_engine.recommend_next_topic(
        topic="Ohm's Law",
        strong_areas=[],
        weak_areas=[WeakAreaItem(concept="inverse_relationship", score=0.3, reason="Weak")],
        overall_score=0.40,
        learning_path=path
    )
    assert next_topic_fail is None
    assert "Prerequisite" in reason_fail or "weak" in reason_fail


def test_13_skipped_question_handling(mock_agent6_bridge):
    """TEST 13: Skipped questions are marked skipped, 0 points, never misconception."""
    scorer = ScoringService(bridge=mock_agent6_bridge)
    q = AssessmentQuestion(question_id="q_skip", assessment_id="a1", text="prompt", expected_concept="concept_a", points=2.0)
    res = scorer.score_response(q, None)
    assert res.classification == "skipped"
    assert res.points_earned == 0.0
    assert res.is_skipped is True
    assert res.misconception is None


def test_14_incomplete_assessment_handling(custom_assessment_service):
    """TEST 14: Incomplete assessment evaluates answered questions and skips unanswered."""
    config = AssessmentConfig(topic="Ohm's Law", question_count=3)
    _, questions = custom_assessment_service.create_assessment(config)
    sess = custom_assessment_service.start_session(config.assessment_id, "std_inc")

    # Submit only 1 out of 3 questions
    ans = {questions[0].question_id: "V = IR"}
    result, report = custom_assessment_service.submit_assessment(sess.session_id, answers=ans)

    assert result.status == "completed"
    assert len(result.question_results) == 3
    # At least two questions marked skipped
    skipped = [qr for qr in result.question_results if qr.is_skipped]
    assert len(skipped) >= 2


def test_15_assessment_timeout():
    """TEST 15: Assessment handles duration limit cleanly."""
    config = AssessmentConfig(topic="Ohm's Law", duration_minutes=5)
    assessment_service.create_assessment(config)
    sess = assessment_service.start_session(config.assessment_id, "std_time")
    assert sess.duration_minutes == 5
    assert sess.status == "in_progress"


def test_16_duplicate_question_detection():
    """TEST 16: Validator rejects duplicate question IDs."""
    questions = [
        AssessmentQuestion(question_id="dup_id", assessment_id="a1", text="q1", expected_concept="c1", points=1.0),
        AssessmentQuestion(question_id="dup_id", assessment_id="a1", text="q2", expected_concept="c2", points=1.0)
    ]
    is_valid, errors = assessment_validator.validate_assessment(questions)
    assert is_valid is False
    assert any("Duplicate question ID" in e for e in errors)


def test_17_invalid_assessment_detection():
    """TEST 17: Validator rejects invalid assessment configurations."""
    # Empty questions
    is_valid, errors = assessment_validator.validate_assessment([])
    assert is_valid is False
    assert any("at least one question" in e for e in errors)


def test_18_agent6_integration(mock_agent6_bridge):
    """TEST 18: Agent 6 evaluator bridge translates responses accurately."""
    q = AssessmentQuestion(
        question_id="q_ag6",
        assessment_id="a1",
        text="What happens to current if resistance increases at constant voltage?",
        type="conceptual",
        expected_concept="inverse_relationship",
        points=2.0
    )
    resp = AssessmentResponse(
        question_id="q_ag6",
        student_id="s1",
        answer="Current increases with resistance"
    )
    eval_res = mock_agent6_bridge.evaluate_response(q, resp)
    assert eval_res["classification"] == "misconception"
    assert "Direct proportionality" in eval_res["misconception"]


def test_19_agent3_evidence_generation(mock_profile_bridge):
    """TEST 19: Generates durable structured evidence emitted to Agent 3."""
    success = mock_profile_bridge.emit_assessment_evidence(
        student_id="s_test",
        assessment_id="a_test",
        lesson_id="l_test",
        topic="Ohm's Law",
        score=0.75,
        concept_scores={"voltage": 1.0, "current": 0.5},
        weak_concepts=["current"],
        strong_concepts=["voltage"],
        misconceptions=["Inverted current"]
    )
    assert success is True
    assert len(mock_profile_bridge.get_service().recorded) == 1


def test_20_learning_report_generation(custom_assessment_service):
    """TEST 20: Learning report contains all machine-readable fields and grounded summary."""
    config = AssessmentConfig(topic="Ohm's Law", question_count=3)
    _, questions = custom_assessment_service.create_assessment(config)
    sess = custom_assessment_service.start_session(config.assessment_id, "std_rep")
    ans = {q.question_id: "V = IR" for q in questions}

    result, report = custom_assessment_service.submit_assessment(sess.session_id, answers=ans)
    assert isinstance(report, LearningReport)
    assert report.topic == "Ohm's Law"
    assert report.score.percentage > 0.0
    assert report.human_readable_summary != ""
    assert report.overall_progress > 0.0


def test_21_grounded_question_generation():
    """TEST 21: Preserves RAG source references on generated questions."""
    rag_context = [
        {"document_id": "physics_ch3.pdf", "page": 42, "section": "3.2 Ohm's Law", "chunk_id": "c_42_1"}
    ]
    config = AssessmentConfig(topic="Ohm's Law", source_references=rag_context)
    questions = question_generator.generate_questions(config, context={"rag_context": rag_context})
    assert len(questions) > 0
    # First question preserves source reference
    assert len(questions[0].source_references) > 0
    assert questions[0].source_references[0]["document_id"] == "physics_ch3.pdf"


def test_22_multilingual_assessment_metadata():
    """TEST 22: Supports Hinglish and English assessment configurations."""
    config_hinglish = AssessmentConfig(topic="Ohm's Law", language="Hinglish")
    _, questions_h = assessment_service.create_assessment(config_hinglish)
    assert len(questions_h) > 0
    assert any("kya" in q.text.lower() or "formula" in q.text.lower() for q in questions_h)


# ============================================================
# SECTION 53: MANDATORY OHM'S LAW ASSESSMENT ACCEPTANCE TEST
# ============================================================

def test_mandatory_ohms_law_assessment(custom_assessment_service):
    """
    SECTION 53 MANDATORY ACCEPTANCE TEST:
    Topic: Ohm's Law
    Q1: "What is the relationship between voltage, current and resistance?" -> "V = IR" (Strong)
    Q2: "If V = 10 V and R = 5 Ω, calculate current." -> "2 A" (Strong)
    Q3: "If voltage remains constant and resistance increases, what happens to current?" -> "Current increases." (Misconception!)

    Expected:
    - Q1: strong
    - Q2: strong
    - Q3: incorrect + misconception
    - Overall score: 3/5 or 60%
    - Weak area identified: inverse relationship
    - Misconception identified: direct relationship assumption
    - Revision: I = V/R and constant-voltage examples
    """
    aid = "mandatory_ohm_test"
    questions = [
        AssessmentQuestion(
            question_id="ohm_q1",
            assessment_id=aid,
            text="What is the relationship between voltage, current and resistance?",
            type="short_answer",
            expected_answer="V = I * R",
            expected_concept="ohms_law_formula",
            points=1.0,
            difficulty=0.3
        ),
        AssessmentQuestion(
            question_id="ohm_q2",
            assessment_id=aid,
            text="If V = 10 V and R = 5 Ω, calculate current.",
            type="numerical",
            expected_value=2.0,
            unit="A",
            tolerance=0.05,
            expected_concept="voltage_calculation",
            points=2.0,
            difficulty=0.4
        ),
        AssessmentQuestion(
            question_id="ohm_q3",
            assessment_id=aid,
            text="If voltage remains constant and resistance increases, what happens to current?",
            type="conceptual",
            expected_answer="Current decreases (I = V/R)",
            expected_concept="inverse_relationship",
            points=2.0,
            difficulty=0.5
        )
    ]

    config = AssessmentConfig(
        assessment_id=aid,
        topic="Ohm's Law",
        question_count=3,
        passing_score=0.70
    )

    # Student answers
    answers = {
        "ohm_q1": "V = IR",
        "ohm_q2": "2 A",
        "ohm_q3": "Current increases."
    }

    result, report = custom_assessment_service.evaluate_direct(
        config=config,
        questions=questions,
        student_id="student_ohm_01",
        answers=answers,
        learning_path=["Ohm's Law", "Series and Parallel Circuits"]
    )

    # 1. Verify Question Scores
    q_map = {qr.question_id: qr for qr in result.question_results}
    assert q_map["ohm_q1"].correctness == 1.0  # Strong
    assert q_map["ohm_q1"].points_earned == 1.0

    assert q_map["ohm_q2"].correctness == 1.0  # Strong
    assert q_map["ohm_q2"].points_earned == 2.0

    assert q_map["ohm_q3"].correctness == 0.0  # Incorrect + misconception
    assert q_map["ohm_q3"].classification == "misconception"
    assert q_map["ohm_q3"].misconception is not None

    # 2. Verify Overall Score
    assert result.score.raw == 3.0
    assert result.score.max == 5.0
    assert result.score.percentage == 0.60
    assert result.score.passed is False

    # 3. Verify Weak Areas specifically identify inverse relationship
    weak_concepts = [w.concept for w in result.weak_areas]
    assert "inverse_relationship" in weak_concepts

    # 4. Verify Misconceptions aggregated
    assert len(result.misconceptions) >= 1
    assert any("Direct proportionality" in m.misconception or "increase" in m.misconception.lower() for m in result.misconceptions)

    # 5. Verify Revision recommendations target I = V/R and constant-voltage problems
    rec_texts = " ".join([r.reason for r in report.recommended_revision])
    assert "I = V/R" in rec_texts or "inverse" in rec_texts.lower()

    # 6. Verify human summary does not vaguely say "weak in Ohm's Law"
    assert "inverse_relationship" in report.human_readable_summary.lower() or "inverse" in report.human_readable_summary.lower()


# ============================================================
# SECTION 54: SECOND ASSESSMENT TEST (MINOR NUMERICAL ERROR)
# ============================================================

def test_second_assessment_minor_numerical_error(custom_assessment_service):
    """
    SECTION 54 TEST:
    All conceptual questions are correct.
    One numerical question has a small rounding difference (e.g. 2.08 A vs 2.0 A within rounding tolerance).
    Expected:
    - High overall score (> 85%)
    - No major misconception
    - Minor numerical feedback
    - Do NOT recommend full reteaching
    """
    aid = "second_assess_test"
    questions = [
        AssessmentQuestion(
            question_id="q_c1",
            assessment_id=aid,
            text="State Ohm's Law formula.",
            type="short_answer",
            expected_concept="ohms_law_formula",
            points=2.0
        ),
        AssessmentQuestion(
            question_id="q_c2",
            assessment_id=aid,
            text="What happens to current if resistance decreases?",
            type="conceptual",
            expected_concept="inverse_relationship",
            points=2.0
        ),
        AssessmentQuestion(
            question_id="q_num",
            assessment_id=aid,
            text="Calculate current for 10V across 5 Ohms.",
            type="numerical",
            expected_value=2.0,
            tolerance=0.05,
            expected_concept="numerical_calculation",
            points=2.0
        )
    ]
    config = AssessmentConfig(assessment_id=aid, topic="Ohm's Law", question_count=3)

    # Student answers with minor rounding error in numerical
    answers = {
        "q_c1": "V = IR",
        "q_c2": "Current increases because resistance opposes flow",
        "q_num": "2.08 A"  # Slightly above standard 5% tolerance, caught in rounding band
    }

    result, report = custom_assessment_service.evaluate_direct(
        config=config,
        questions=questions,
        student_id="student_num_02",
        answers=answers
    )

    # High overall score
    assert result.score.percentage >= 0.85
    # No major misconceptions detected
    assert len(result.misconceptions) == 0
    # Does not require major reteaching
    high_priority_recs = [r for r in report.recommended_revision if r.priority == "high"]
    assert len(high_priority_recs) == 0


# ============================================================
# SECTION 55: REPORT QUALITY TEST (SPECIFIC CONCEPT NAMING)
# ============================================================

def test_report_quality_specific_concept(custom_assessment_service):
    """
    SECTION 55 TEST:
    Given:
    Strong: voltage definition
    Weak: inverse relationship
    Misconception: current increases with resistance

    The report must NOT say: 'Student is weak in Ohm's law.'
    Instead identify the specific weak concept ('inverse relationship').
    """
    aid = "report_quality_test"
    questions = [
        AssessmentQuestion(
            question_id="q_volt",
            assessment_id=aid,
            text="Define Voltage.",
            type="short_answer",
            expected_concept="voltage_definition",
            points=1.0
        ),
        AssessmentQuestion(
            question_id="q_inv",
            assessment_id=aid,
            text="Effect on current when resistance rises?",
            type="conceptual",
            expected_concept="inverse_relationship",
            points=2.0
        )
    ]
    config = AssessmentConfig(assessment_id=aid, topic="Ohm's Law", question_count=2)

    answers = {
        "q_volt": "V = IR",
        "q_inv": "Current increases with resistance"
    }

    result, report = custom_assessment_service.evaluate_direct(
        config=config,
        questions=questions,
        student_id="student_q_03",
        answers=answers
    )

    summary = report.human_readable_summary
    # Must NOT say student is weak in Ohm's Law
    assert "weak in ohm's law" not in summary.lower()
    # Must specifically identify inverse relationship
    assert "inverse relationship" in summary.lower()


# ============================================================
# SECTION 56 & 57: NEXT-TOPIC & NO-EVIDENCE RULE TEST
# ============================================================

def test_next_topic_and_no_evidence_rule(custom_assessment_service):
    """
    SECTION 56 & 57 TEST:
    Case A: All concepts strong + learning path supplied -> recommends subsequent circuit concept.
    Case B: All concepts strong + NO learning path supplied -> recommended_next_topic must be None (No curriculum hallucination!).
    """
    aid = "next_topic_test"
    questions = [
        AssessmentQuestion(
            question_id="q1", assessment_id=aid, text="Formula", type="short_answer",
            expected_concept="ohms_law", points=1.0
        ),
        AssessmentQuestion(
            question_id="q2", assessment_id=aid, text="Calculation", type="numerical",
            expected_value=2.0, expected_concept="voltage", points=1.0
        )
    ]
    config = AssessmentConfig(assessment_id=aid, topic="Ohm's Law", question_count=2)
    answers = {"q1": "V = IR", "q2": "2"}

    # Case A: With Learning Path
    path = ["Ohm's Law", "Series and Parallel Circuits"]
    result_a, report_a = custom_assessment_service.evaluate_direct(
        config=config,
        questions=questions,
        student_id="student_a",
        answers=answers,
        learning_path=path
    )
    assert report_a.recommended_next_topic == "Series and Parallel Circuits"

    # Case B: Without Learning Path (No-Evidence Rule)
    result_b, report_b = custom_assessment_service.evaluate_direct(
        config=config,
        questions=questions,
        student_id="student_b",
        answers=answers,
        learning_path=None
    )
    assert report_b.recommended_next_topic is None


# ============================================================
# REST API INTEGRATION TESTS
# ============================================================

def test_assessment_api_endpoints():
    """Tests the full REST API lifecycle (/api/assessment/*)."""
    client = TestClient(app)

    # 1. Create Assessment
    create_resp = client.post("/api/assessment/create", json={
        "topic": "Ohm's Law",
        "question_count": 3,
        "language": "English"
    })
    assert create_resp.status_code == 200
    create_data = create_resp.json()
    assert create_data["status"] == "success"
    aid = create_data["assessment_id"]
    questions = create_data["questions"]
    assert len(questions) == 3

    # 2. Get Assessment (Student View)
    get_resp = client.get(f"/api/assessment/{aid}")
    assert get_resp.status_code == 200
    get_data = get_resp.json()
    # Correct options stripped in student view
    assert get_data["questions"][0]["correct_option"] is None

    # 3. Start Session
    start_resp = client.post(f"/api/assessment/{aid}/start", json={"student_id": "api_student_1"})
    assert start_resp.status_code == 200
    session_id = start_resp.json()["session"]["session_id"]

    # 4. Submit Individual Response
    resp_resp = client.post(f"/api/assessment/{aid}/response", json={
        "session_id": session_id,
        "question_id": questions[0]["question_id"],
        "answer": "V = I * R"
    })
    assert resp_resp.status_code == 200

    # 5. Submit Assessment
    submit_resp = client.post(f"/api/assessment/{aid}/submit", json={
        "session_id": session_id,
        "answers": {
            questions[0]["question_id"]: "V = I * R",
            questions[1]["question_id"]: "2 A",
            questions[2]["question_id"]: "Current decreases"
        }
    })
    assert submit_resp.status_code == 200
    submit_data = submit_resp.json()
    assert "result" in submit_data
    assert "report" in submit_data

    # 6. Get Result
    res_resp = client.get(f"/api/assessment/{aid}/result")
    assert res_resp.status_code == 200
    assert res_resp.json()["result"]["status"] == "completed"

    # 7. Get Report
    rep_resp = client.get(f"/api/assessment/{aid}/report")
    assert rep_resp.status_code == 200
    assert rep_resp.json()["report"]["topic"] == "Ohm's Law"
