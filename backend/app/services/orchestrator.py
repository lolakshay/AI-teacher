"""
Teaching Orchestrator Subsystem
Main State Machine and Loop Controller:
UNDERSTAND -> PLAN -> EXPLAIN -> DEMONSTRATE -> QUESTION -> EVALUATE -> ADAPT -> CONTINUE -> ASSESSMENT -> REPORT

Maintains session state, step progression, loop protection, and coordinates between subsystems.
"""

import uuid
import logging
from typing import Dict, Optional, Tuple, Any
from backend.app.core.config import settings
from backend.app.core.models import (
    SessionState, StudentProfile, LearningRequest, LessonPlan,
    TeachingStep, StudentResponse, EvaluationResult, LearningReport
)
from backend.app.services.lesson_planner import lesson_planner
from backend.app.services.evaluation_engine import evaluation_engine
from backend.app.services.adaptation_engine import adaptation_engine
from backend.app.services.assessment_engine import assessment_engine

logger = logging.getLogger("ai_teacher.orchestrator")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] [%(name)s] %(message)s")


class TeachingOrchestrator:
    def __init__(self):
        self.sessions: Dict[str, SessionState] = {}

    def create_session(self, request: LearningRequest, profile: Optional[StudentProfile] = None) -> SessionState:
        session_id = str(uuid.uuid4())[:8]
        if profile is None:
            profile = StudentProfile(
                student_id=request.student_id,
                educational_level=request.educational_level,
                preferred_language=request.preferred_language,
                preferred_teaching_style=request.teaching_style,
                preferred_depth=request.desired_depth
            )

        # Plan the lesson
        plan, initial_steps = lesson_planner.create_lesson_plan(request, profile)

        session = SessionState(
            session_id=session_id,
            student_profile=profile,
            learning_request=request,
            lesson_plan=plan,
            current_step_index=0,
            steps=initial_steps,
            current_concept=initial_steps[0].concept_id if initial_steps else plan.topic,
            status="teaching"
        )
        self.sessions[session_id] = session

        logger.info(
            f"[SESSION_STARTED] session_id={session_id} student_id={request.student_id} "
            f"topic='{request.topic}' lang={request.preferred_language} duration={request.available_time}m"
        )
        for idx, step in enumerate(initial_steps):
            logger.info(
                f"[TEACHING_STEP_CREATED] session_id={session_id} step_index={idx} "
                f"step_id={step.step_id} type={step.step_type} concept='{step.concept_id}'"
            )

        return session

    def get_session(self, session_id: str) -> Optional[SessionState]:
        return self.sessions.get(session_id)

    def get_current_step(self, session_id: str) -> Optional[TeachingStep]:
        session = self.get_session(session_id)
        if not session or not session.steps:
            return None
        if session.current_step_index < len(session.steps):
            step = session.steps[session.current_step_index]
            if step.step_type == "question":
                logger.info(
                    f"[QUESTION_PRESENTED] session_id={session_id} step_id={step.step_id} "
                    f"concept='{step.concept_id}' prompt='{step.question.prompt if step.question else ''}'"
                )
            return step
        return None

    def advance_step(self, session_id: str) -> Tuple[Optional[TeachingStep], str]:
        """Advances teaching to the next step or transitions to assessment."""
        session = self.get_session(session_id)
        if not session:
            return None, "session_not_found"

        session.current_step_index += 1
        if session.current_step_index < len(session.steps):
            step = session.steps[session.current_step_index]
            session.current_concept = step.concept_id
            session.status = "questioning" if step.step_type in ["question", "re_explanation"] else "teaching"
            logger.info(
                f"[TEACHING_STEP_ADVANCED] session_id={session_id} step_index={session.current_step_index} "
                f"step_id={step.step_id} type={step.step_type} status={session.status}"
            )
            return step, session.status
        else:
            session.status = "assessment"
            logger.info(f"[ASSESSMENT_TRANSITION] session_id={session_id} ready_for_assessment")
            return None, "assessment"

    def handle_student_response(self, response: StudentResponse) -> Dict[str, Any]:
        """
        Receives student response, performs evaluation, enforces loop protection,
        and triggers adaptation or continuation while updating the learner model.
        """
        session = self.get_session(response.session_id)
        if not session:
            raise ValueError(f"Session {response.session_id} not found")

        current_step = self.get_current_step(response.session_id)
        if not current_step:
            raise ValueError("No active step to respond to")

        logger.info(
            f"[RESPONSE_RECEIVED] session_id={response.session_id} question_id={response.question_id} "
            f"answer='{response.student_answer}'"
        )

        # 1. EVALUATE
        evaluation = evaluation_engine.evaluate(
            response=response,
            current_step=current_step,
            language=session.learning_request.preferred_language
        )
        session.evaluations.append(evaluation)

        logger.info(
            f"[RESPONSE_EVALUATED] session_id={response.session_id} correct={evaluation.correctness} "
            f"misconception={evaluation.misconception} action={evaluation.recommended_action}"
        )

        # Notify Agent 3 (Personalization / Learner Model) of formative response
        try:
            from backend.personalization.service import personalization_service
            personalization_service.update_concept_knowledge(
                student_id=session.learning_request.student_id,
                concept_id=current_step.concept_id,
                evidence={
                    "source": "lesson_response",
                    "session_id": session.session_id,
                    "question_id": response.question_id,
                    "correctness": 1.0 if evaluation.correctness else 0.0,
                    "misconception": evaluation.misconception,
                    "confidence": evaluation.confidence,
                    "details": {"teacher_thought": evaluation.teacher_thought}
                }
            )
            logger.info(f"[LEARNER_UPDATED] student_id={session.learning_request.student_id} concept='{current_step.concept_id}'")
        except Exception as e:
            logger.debug(f"Learner model update skipped or in-memory fallback: {e}")

        # 2. ADAPT or CONTINUE (with Section 20 Loop Protection)
        if not evaluation.correctness or evaluation.recommended_action in ["give_analogy", "simplify", "re_explain"]:
            concept_key = current_step.concept_id
            attempts = session.reteach_attempts_by_concept.get(concept_key, 0) + 1
            session.reteach_attempts_by_concept[concept_key] = attempts

            if attempts > settings.MAX_RETEACH_ATTEMPTS:
                # LOOP PROTECTION TRIGGERED: Prevent infinite loop
                logger.warning(
                    f"[LOOP_PROTECTION_TRIGGERED] session_id={session.session_id} concept='{concept_key}' "
                    f"attempts={attempts} > max={settings.MAX_RETEACH_ATTEMPTS}. Scaffolded resolution."
                )
                scaffold_step = TeachingStep(
                    step_id=f"scaffold_{uuid.uuid4().hex[:6]}",
                    lesson_id=current_step.lesson_id,
                    concept_id=concept_key,
                    step_type="summary",
                    objective=f"Consolidate prerequisite intuition for {concept_key}",
                    explanation=(
                        f"We noticed this relationship ({concept_key}) can be tricky! Let's remember the foundational rule: "
                        f"when resistance opposes flow, current decreases (I = V / R). We will bookmark this for targeted revision."
                    ),
                    language=session.learning_request.preferred_language,
                    difficulty="beginner",
                    avatar_emotion="encouraging"
                )
                insert_pos = session.current_step_index + 1
                session.steps.insert(insert_pos, scaffold_step)
                session.current_step_index = insert_pos
                session.status = "teaching"

                return {
                    "evaluation": evaluation,
                    "next_step": scaffold_step,
                    "session_status": session.status,
                    "adaptation_occurred": True,
                    "loop_protection_triggered": True,
                    "misconception_detected": evaluation.misconception
                }

            # Normal adaptive intervention
            adaptive_step = adaptation_engine.create_adaptation_step(
                evaluation=evaluation,
                current_step=current_step,
                language=session.learning_request.preferred_language
            )

            insert_pos = session.current_step_index + 1
            session.steps.insert(insert_pos, adaptive_step)
            session.current_step_index = insert_pos
            session.active_misconception = evaluation.misconception
            session.adaptation_count += 1
            session.status = "adapting"

            logger.info(
                f"[ADAPTATION_TRIGGERED] session_id={session.session_id} strategy='{adaptive_step.step_type}' "
                f"misconception='{evaluation.misconception}' new_step_id={adaptive_step.step_id}"
            )

            return {
                "evaluation": evaluation,
                "next_step": adaptive_step,
                "session_status": session.status,
                "adaptation_occurred": True,
                "loop_protection_triggered": False,
                "misconception_detected": evaluation.misconception
            }
        else:
            # Correct understanding -> advance forward
            session.active_misconception = None
            next_step, new_status = self.advance_step(session.session_id)

            return {
                "evaluation": evaluation,
                "next_step": next_step,
                "session_status": new_status,
                "adaptation_occurred": False,
                "loop_protection_triggered": False,
                "misconception_detected": None
            }

    def set_session_language(self, session_id: str, language: str) -> Optional[SessionState]:
        """
        Dynamic Multilingual Adaptation (Section 21):
        Switches preferred language on-the-fly while strictly preserving:
        topic, concept, lesson position, learner state, and assessment context.
        """
        session = self.get_session(session_id)
        if not session:
            return None

        session.learning_request.preferred_language = language
        if session.student_profile:
            session.student_profile.preferred_language = language

        # Update remaining steps' language
        for i in range(session.current_step_index, len(session.steps)):
            session.steps[i].language = language

        logger.info(f"[MULTILINGUAL_ADAPTED] session_id={session_id} new_language={language}")
        return session

    def start_assessment(self, session_id: str):
        session = self.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        logger.info(f"[ASSESSMENT_STARTED] session_id={session_id}")
        questions = assessment_engine.generate_assessment(session)
        session.status = "assessment"
        return questions

    def complete_assessment(self, session_id: str, quiz_answers: Optional[Dict[str, str]] = None) -> LearningReport:
        session = self.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        report = assessment_engine.compile_learning_report(session, quiz_answers)
        session.learning_report = report
        session.status = "completed"

        logger.info(
            f"[ASSESSMENT_COMPLETED] session_id={session_id} score={report.score}% "
            f"misconceptions={len(report.misconceptions)} next_topic='{report.recommended_next_topic}'"
        )

        # Wire update into Agent 3 (Learner Profile Repository)
        try:
            from backend.personalization.service import personalization_service
            personalization_service.record_assessment_result(
                student_id=session.learning_request.student_id,
                assessment_data={
                    "assessment_id": f"ass_{session_id}",
                    "lesson_id": report.lesson_id,
                    "topic": session.learning_request.topic or "Ohm's Law",
                    "score": report.score,
                    "concept_scores": {
                        session.current_concept or "circuit_dynamics": report.score / 100.0
                    },
                    "weak_concepts": report.weak_areas,
                    "strong_concepts": report.concepts_understood,
                    "misconceptions": report.misconceptions
                }
            )
            logger.info(f"[LEARNER_UPDATED] student_id={session.learning_request.student_id} assessment recorded in SQLite")
        except Exception as e:
            logger.debug(f"Learner update persisted locally: {e}")

        return report

    def switch_language(self, session_id: str, target_language: str, teaching_style: Optional[str] = None) -> SessionState:
        """
        Switches the session's active teaching language without restarting the lesson.
        Preserves topic, current concept, lesson position, learner profile, and assessment state.
        """
        session = self.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        from backend.multilingual.services.language_service import language_service
        language_service.switch_session_language(session_id, target_language, teaching_style)
        return session

orchestrator = TeachingOrchestrator()


