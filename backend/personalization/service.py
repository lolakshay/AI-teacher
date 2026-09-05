"""
PersonalizationService Facade conforming to Sections 11, 20-25, 45-48.
Central coordination point providing stable clean integration interfaces for:
- Agent 1 (Teaching Brain / Orchestrator)
- Agent 6 (Response Evaluator)
- Agent 7 (Assessment Engine)
- Agent 8 (Language Specialist)
- REST API / Frontend
"""

from typing import Optional, Dict, Any, List, Union
from datetime import datetime, timezone

from backend.personalization.schemas import (
    StudentProfile, StudentPreferences, LearnerKnowledge,
    LearnerEvidence, MisconceptionRecord, LearningHistoryEntry,
    AssessmentHistoryEntry, PersonalizationContext,
    CreateProfileRequest, UpdateProfileRequest, KnowledgeUpdateEvidence
)
from backend.personalization.mastery_model import mastery_model, MasteryModel
from backend.personalization.engine import personalization_engine, PersonalizationEngine
from backend.personalization.repository import (
    profile_repository, StudentProfileRepository, SQLiteProfileRepository
)


class PersonalizationService:
    """
    Subsystem Service Facade for Part 3.
    Thread-safe, decoupled, explainable, and zero hidden LLM dependency.
    """

    def __init__(
        self,
        repository: Optional[StudentProfileRepository] = None,
        model: Optional[MasteryModel] = None,
        engine: Optional[PersonalizationEngine] = None
    ):
        self.repository = repository or profile_repository
        self.mastery_model = model or mastery_model
        self.engine = engine or personalization_engine

    # ----------------- AGENT 1 INTEGRATION (Sections 11 & 45) -----------------

    def get_personalization_context(
        self,
        student_id: str,
        topic: Optional[str] = None,
        request: Optional[Any] = None
    ) -> PersonalizationContext:
        """
        Retrieves compact, actionable PersonalizationContext for Agent 1.
        Does NOT dump entire lifetime history to the LLM.
        """
        profile = self.repository.get_profile(student_id)
        if not profile:
            # Create standard default beginner profile
            profile = StudentProfile(
                student_id=student_id,
                educational_level="beginner",
                preferred_language="English",
                preferred_teaching_style="analogy_based",
                preferred_depth="standard"
            )
            self.repository.create_profile(profile)

        return self.engine.generate_context(profile, topic=topic, current_request=request)

    # ----------------- AGENT 6 INTEGRATION (Sections 21, 22, 46) -----------------

    def update_concept_knowledge(
        self,
        student_id: str,
        concept_id: str,
        evidence: Union[LearnerEvidence, KnowledgeUpdateEvidence, Dict[str, Any], Any]
    ) -> LearnerKnowledge:
        """
        Agent 6 evaluates; Agent 3 remembers.
        Converts in-lesson evaluation results into durable learner evidence and updates mastery.
        """
        # 1. Normalize evidence input
        if isinstance(evidence, LearnerEvidence):
            norm_evidence = evidence
        elif isinstance(evidence, KnowledgeUpdateEvidence):
            res = "misconception" if evidence.misconception else ("correct" if evidence.correctness >= 0.7 else "incorrect")
            norm_evidence = LearnerEvidence(
                source=evidence.source,
                session_id=evidence.session_id,
                question_id=evidence.question_id,
                result=res,
                score=evidence.correctness,
                confidence=evidence.confidence,
                misconception=evidence.misconception,
                details=evidence.details
            )
        elif isinstance(evidence, dict):
            correctness = float(evidence.get("correctness", 0.0))
            classification = evidence.get("classification", "correct" if correctness >= 0.7 else "incorrect")
            misconception = evidence.get("misconception")
            norm_evidence = LearnerEvidence(
                source=evidence.get("source", "lesson_response"),
                session_id=evidence.get("session_id"),
                question_id=evidence.get("question_id"),
                result=classification,
                score=correctness,
                confidence=float(evidence.get("confidence", 1.0)),
                misconception=misconception,
                details=evidence.get("details", {})
            )
        else:
            # Assume EvaluationResult-like object from Agent 6
            correctness = float(getattr(evidence, "correctness", 0.0) if not isinstance(getattr(evidence, "correctness", 0.0), bool) else (1.0 if getattr(evidence, "correctness") else 0.0))
            classification = str(getattr(evidence, "classification", "correct" if correctness >= 0.7 else "incorrect"))
            misconception = getattr(evidence, "misconception", None)
            confidence = float(getattr(evidence, "confidence", 1.0))
            norm_evidence = LearnerEvidence(
                source="lesson_response",
                result=classification,
                score=correctness,
                confidence=confidence,
                misconception=misconception,
                details={"teacher_thought": getattr(evidence, "teacher_thought", "")}
            )

        # 2. Retrieve existing concept knowledge
        existing_knowledge_map = self.repository.get_knowledge_state(student_id, concept_id)
        current_knowledge = existing_knowledge_map.get(concept_id)
        concept_name = current_knowledge.concept_name if current_knowledge else concept_id.replace("_", " ").title()

        # 3. Apply explainable deterministic mastery update
        updated_knowledge = self.mastery_model.update_mastery(
            current_knowledge=current_knowledge,
            concept_id=concept_id,
            concept_name=concept_name,
            evidence=norm_evidence
        )

        # 4. Persist to repository
        return self.repository.save_knowledge_state(student_id, updated_knowledge)

    # ----------------- AGENT 7 INTEGRATION (Sections 23 & 47) -----------------

    def record_assessment_result(
        self,
        student_id: str,
        assessment_data: Union[AssessmentHistoryEntry, Dict[str, Any], Any]
    ) -> AssessmentHistoryEntry:
        """
        Agent 7 assessment ingestion.
        Updates concept mastery scores, updates strong/weak concepts, and stores assessment history.
        """
        if isinstance(assessment_data, AssessmentHistoryEntry):
            entry = assessment_data
        elif isinstance(assessment_data, dict):
            entry = AssessmentHistoryEntry(
                assessment_id=assessment_data.get("assessment_id", f"ass_{int(datetime.now().timestamp())}"),
                lesson_id=assessment_data.get("lesson_id", ""),
                topic=assessment_data.get("topic", ""),
                score=float(assessment_data.get("score", 0.0)),
                concept_scores={k: float(v) for k, v in assessment_data.get("concept_scores", {}).items()},
                weak_concepts=assessment_data.get("weak_concepts", []),
                strong_concepts=assessment_data.get("strong_concepts", []),
                misconceptions=assessment_data.get("misconceptions", [])
            )
        else:
            entry = AssessmentHistoryEntry(
                assessment_id=getattr(assessment_data, "assessment_id", f"ass_{int(datetime.now().timestamp())}"),
                lesson_id=getattr(assessment_data, "lesson_id", ""),
                topic=getattr(assessment_data, "topic", ""),
                score=float(getattr(assessment_data, "score", 0.0)),
                concept_scores=getattr(assessment_data, "concept_scores", {}),
                weak_concepts=getattr(assessment_data, "weak_concepts", []),
                strong_concepts=getattr(assessment_data, "strong_concepts", []),
                misconceptions=getattr(assessment_data, "misconceptions", [])
            )

        # 1. Update concept mastery for each tested concept
        now_iso = datetime.now(timezone.utc).isoformat()
        for c_id, c_score in entry.concept_scores.items():
            ev = LearnerEvidence(
                source="assessment",
                session_id=entry.lesson_id,
                question_id=entry.assessment_id,
                result="correct" if c_score >= 0.7 else "incorrect",
                score=c_score,
                confidence=0.95,
                timestamp=now_iso,
                details={"overall_assessment_score": entry.score}
            )
            self.update_concept_knowledge(student_id, c_id, ev)

        # 2. Record any misconceptions found in assessment
        for misc_text in entry.misconceptions:
            ev = LearnerEvidence(
                source="assessment",
                session_id=entry.lesson_id,
                question_id=entry.assessment_id,
                result="misconception",
                score=0.1,
                confidence=0.95,
                misconception=misc_text,
                timestamp=now_iso
            )
            # Associate to lesson topic or general concept
            c_key = entry.topic.lower().replace(" ", "_") if entry.topic else "general"
            self.update_concept_knowledge(student_id, c_key, ev)

        # 3. Store assessment history
        return self.repository.add_assessment_history(student_id, entry)

    # ----------------- LEARNING HISTORY (Sections 24 & 25) -----------------

    def record_learning_session(
        self,
        student_id: str,
        entry: LearningHistoryEntry
    ) -> LearningHistoryEntry:
        """
        At the end of every completed lesson, stores metadata.
        Does NOT store raw lesson transcripts.
        """
        return self.repository.add_learning_history(student_id, entry)

    def get_recent_learning_history(
        self,
        student_id: str,
        limit: int = 10
    ) -> List[LearningHistoryEntry]:
        return self.repository.get_learning_history(student_id, limit=limit)

    def get_topic_history(
        self,
        student_id: str,
        topic: str
    ) -> List[LearningHistoryEntry]:
        all_hist = self.repository.get_learning_history(student_id, limit=50)
        topic_lower = topic.lower()
        return [h for h in all_hist if topic_lower in h.topic.lower()]

    # ----------------- AGENT 8 INTEGRATION (Section 48) -----------------

    def get_student_language(self, student_id: str) -> str:
        """Source of truth for explicit student language preference."""
        profile = self.repository.get_profile(student_id)
        if not profile:
            return "English"
        return profile.preferences.preferred_language or profile.preferred_language or "English"

    # ----------------- PROFILE MANAGEMENT (Sections 9, 10, 39, 40) -----------------

    def create_or_update_profile(self, request: CreateProfileRequest) -> StudentProfile:
        existing = self.repository.get_profile(request.student_id)
        if existing:
            # Safe partial update without deleting historical data (Section 9)
            updates: Dict[str, Any] = {}
            if request.educational_level:
                updates["educational_level"] = request.educational_level
            if request.preferred_language:
                updates["preferred_language"] = request.preferred_language
            if request.preferred_teaching_style:
                updates["preferred_teaching_style"] = request.preferred_teaching_style
            if request.preferred_depth:
                updates["preferred_depth"] = request.preferred_depth
            if request.learning_objectives is not None:
                updates["learning_objectives"] = request.learning_objectives
            if request.known_concepts is not None:
                updates["known_concepts"] = request.known_concepts
            if request.preferences:
                updates["preferences"] = request.preferences

            updated = self.repository.update_profile(request.student_id, updates)
            return updated or existing

        pref = StudentPreferences(
            preferred_language=request.preferred_language or "English",
            preferred_teaching_style=request.preferred_teaching_style or "analogy_based",
            preferred_depth=request.preferred_depth or "standard"
        )
        if request.preferences:
            for k, v in request.preferences.items():
                if hasattr(pref, k):
                    setattr(pref, k, v)

        new_profile = StudentProfile(
            student_id=request.student_id,
            educational_level=request.educational_level or "beginner",
            preferred_language=request.preferred_language or "English",
            preferred_teaching_style=request.preferred_teaching_style or "analogy_based",
            preferred_depth=request.preferred_depth or "standard",
            learning_objectives=request.learning_objectives or [],
            known_concepts=request.known_concepts or [],
            preferences=pref
        )

        # Handle explicit student self-reported known concepts (Section 19)
        if request.known_concepts:
            for c in request.known_concepts:
                ev = LearnerEvidence(
                    source="profile_self_report",
                    result="self_reported",
                    score=0.50,
                    confidence=0.40
                )
                self.update_concept_knowledge(request.student_id, c, ev)

        return self.repository.create_profile(new_profile)

    def get_profile(self, student_id: str) -> Optional[StudentProfile]:
        return self.repository.get_profile(student_id)

    def update_profile(self, student_id: str, request: UpdateProfileRequest) -> Optional[StudentProfile]:
        updates = request.model_dump(exclude_unset=True)
        return self.repository.update_profile(student_id, updates)

    def reset_profile(self, student_id: str, reset_type: str) -> bool:
        return self.repository.reset_profile(student_id, reset_type)


# Global singleton instance
personalization_service = PersonalizationService()
