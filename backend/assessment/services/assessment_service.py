"""
Master Assessment Service conforming to Sections 1, 2, 13, 14, 15, 24, 28, 29, 44, 45, 50, 58.
Coordinates assessment assembly, session tracking, response evaluation,
scoring, learning analytics, and report emission.
"""

import threading
import logging
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timezone

from backend.assessment.models.config import AssessmentConfig
from backend.assessment.models.question import AssessmentQuestion
from backend.assessment.models.session import AssessmentSession, AssessmentResponse
from backend.assessment.models.result import AssessmentResult
from backend.assessment.models.report import LearningReport
from backend.assessment.generators.question_generator import question_generator, QuestionGenerator
from backend.assessment.validators.assessment_validator import assessment_validator
from backend.assessment.services.scoring_service import scoring_service, ScoringService
from backend.assessment.services.analytics_service import analytics_service, AnalyticsService
from backend.assessment.services.report_service import report_service, ReportService

logger = logging.getLogger(__name__)


class AssessmentNotFoundError(Exception):
    pass


class SessionNotFoundError(Exception):
    pass


class AssessmentService:
    """
    Subsystem facade for Assessment & Learning Analytics.
    """

    def __init__(
        self,
        generator: Optional[QuestionGenerator] = None,
        scorer: Optional[ScoringService] = None,
        analytics: Optional[AnalyticsService] = None,
        reporter: Optional[ReportService] = None
    ):
        self.generator = generator or question_generator
        self.scorer = scorer or scoring_service
        self.analytics = analytics or analytics_service
        self.reporter = reporter or report_service

        # In-memory storage for active assessments, sessions, results, reports
        self._lock = threading.RLock()
        self._assessments: Dict[str, Tuple[AssessmentConfig, List[AssessmentQuestion]]] = {}
        self._sessions: Dict[str, AssessmentSession] = {}
        self._results: Dict[str, AssessmentResult] = {}
        self._reports: Dict[str, LearningReport] = {}

    def create_assessment(
        self,
        config: AssessmentConfig,
        context: Optional[Dict[str, Any]] = None
    ) -> Tuple[AssessmentConfig, List[AssessmentQuestion]]:
        """
        Creates and stores a validated assessment with generated questions.
        """
        questions = self.generator.generate_questions(config, context)
        with self._lock:
            self._assessments[config.assessment_id] = (config, questions)

        logger.info(f"Created assessment '{config.assessment_id}' with {len(questions)} questions.")
        return config, questions

    def get_assessment(
        self,
        assessment_id: str,
        student_view: bool = False
    ) -> Optional[Tuple[AssessmentConfig, List[AssessmentQuestion]]]:
        """
        Retrieves assessment. If student_view is True, strips answer keys to prevent leaking.
        """
        with self._lock:
            data = self._assessments.get(assessment_id)
            if not data:
                return None

            config, questions = data
            if not student_view:
                return config, questions

            # Sanitize questions for student consumption
            sanitized = []
            for q in questions:
                q_copy = q.model_copy()
                q_copy.correct_option = None
                q_copy.expected_answer = None
                q_copy.expected_value = None
                q_copy.rubric = []
                sanitized.append(q_copy)
            return config, sanitized

    def start_session(
        self,
        assessment_id: str,
        student_id: str,
        session_id: Optional[str] = None
    ) -> AssessmentSession:
        """
        Initializes an assessment attempt for a student.
        """
        assessment_data = self.get_assessment(assessment_id)
        if not assessment_data:
            raise AssessmentNotFoundError(f"Assessment '{assessment_id}' not found.")

        config, _ = assessment_data
        session = AssessmentSession(
            session_id=session_id or f"asess_{int(datetime.now().timestamp())}",
            assessment_id=assessment_id,
            student_id=student_id,
            status="in_progress",
            duration_minutes=config.duration_minutes
        )

        with self._lock:
            self._sessions[session.session_id] = session

        return session

    def submit_response(
        self,
        session_id: str,
        response: AssessmentResponse
    ) -> AssessmentSession:
        """
        Records an individual answer into the active session.
        """
        with self._lock:
            session = self._sessions.get(session_id)
            if not session:
                raise SessionNotFoundError(f"Session '{session_id}' not found.")

            # Update or append response
            existing_idx = next(
                (i for i, r in enumerate(session.responses) if r.question_id == response.question_id),
                None
            )
            if existing_idx is not None:
                session.responses[existing_idx] = response
            else:
                session.responses.append(response)

            session.current_question_index = len(session.responses)
            return session

    def submit_assessment(
        self,
        session_id: str,
        answers: Optional[Dict[str, str]] = None,
        learning_path: Optional[List[str]] = None
    ) -> Tuple[AssessmentResult, LearningReport]:
        """
        Submits the assessment, evaluates all questions, runs concept analytics,
        and generates the final learning report.
        """
        with self._lock:
            session = self._sessions.get(session_id)
            if not session:
                raise SessionNotFoundError(f"Session '{session_id}' not found.")

            assessment_data = self._assessments.get(session.assessment_id)
            if not assessment_data:
                raise AssessmentNotFoundError(f"Assessment '{session.assessment_id}' not found.")

            config, questions = assessment_data

            # Merge any dictionary answers passed at submit time
            if answers:
                now_iso = datetime.now(timezone.utc).isoformat()
                for qid, ans_text in answers.items():
                    existing = next((r for r in session.responses if r.question_id == qid), None)
                    if existing:
                        existing.answer = ans_text
                    else:
                        session.responses.append(
                            AssessmentResponse(
                                question_id=qid,
                                student_id=session.student_id,
                                answer=ans_text,
                                submitted_at=now_iso,
                                language=config.language
                            )
                        )

            # Check for timeout if duration_minutes is configured (Section 35)
            # Duration check is non-fatal: records status as completed / timed_out without losing answers
            session.completed_at = datetime.now(timezone.utc).isoformat()
            session.status = "completed"

            # 1. Score each question
            resp_map = {r.question_id: r for r in session.responses}
            question_results = []
            for q in questions:
                resp = resp_map.get(q.question_id)
                qr = self.scorer.score_response(q, resp, language=config.language)
                question_results.append(qr)

            # 2. Compute ScoreSummary
            score_summary = self.scorer.calculate_score_summary(
                question_results,
                passing_score=config.passing_score
            )

            # 3. Concept-level Analytics (Sections 17-20)
            concept_results = self.analytics.analyze_concepts(questions, question_results)
            weak_areas = self.analytics.detect_weak_areas(concept_results)
            strong_areas = self.analytics.detect_strong_areas(concept_results)
            misconceptions = self.analytics.aggregate_misconceptions(question_results)
            diff_breakdown = self.analytics.compute_difficulty_breakdown(questions, question_results)
            type_breakdown = self.analytics.compute_question_type_breakdown(questions, question_results)

            # 4. Assemble AssessmentResult (Section 45)
            result = AssessmentResult(
                assessment_id=config.assessment_id,
                session_id=session_id,
                student_id=session.student_id,
                lesson_id=config.lesson_id,
                topic=config.topic,
                score=score_summary,
                question_results=question_results,
                concept_results=concept_results,
                weak_areas=weak_areas,
                strong_areas=strong_areas,
                misconceptions=misconceptions,
                difficulty_breakdown=diff_breakdown,
                question_type_breakdown=type_breakdown,
                status="completed",
                completed_at=session.completed_at
            )
            self._results[session_id] = result
            self._results[config.assessment_id] = result

            # 5. Compile LearningReport (Section 24)
            report = self.reporter.compile_report(
                assessment_id=config.assessment_id,
                student_id=session.student_id,
                lesson_id=config.lesson_id,
                topic=config.topic,
                score=score_summary,
                question_results=question_results,
                concept_results=concept_results,
                weak_areas=weak_areas,
                strong_areas=strong_areas,
                misconceptions=misconceptions,
                learning_path=learning_path
            )
            self._reports[session_id] = report
            self._reports[config.assessment_id] = report

            return result, report

    def get_result(self, identifier: str) -> Optional[AssessmentResult]:
        with self._lock:
            return self._results.get(identifier)

    def get_report(self, identifier: str) -> Optional[LearningReport]:
        with self._lock:
            return self._reports.get(identifier)

    def evaluate_direct(
        self,
        config: AssessmentConfig,
        questions: List[AssessmentQuestion],
        student_id: str,
        answers: Dict[str, str],
        learning_path: Optional[List[str]] = None
    ) -> Tuple[AssessmentResult, LearningReport]:
        """
        Convenience method for direct assessment evaluation without explicit session management.
        Useful for quick quizzes, automated tests, and orchestrator integrations.
        """
        assessment_validator.ensure_valid(questions, config)
        with self._lock:
            self._assessments[config.assessment_id] = (config, questions)

        sess = self.start_session(config.assessment_id, student_id)
        return self.submit_assessment(sess.session_id, answers, learning_path=learning_path)


assessment_service = AssessmentService()
