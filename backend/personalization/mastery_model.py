"""
Deterministic Explainable Concept Mastery Model conforming to Sections 14-19.
Calculates concept mastery scores, tracks confidence, updates learning status,
and maintains misconception history with resolution tracking.
"""

from typing import Optional, Tuple, List
from datetime import datetime, timezone
from backend.personalization.schemas import (
    LearnerKnowledge, LearnerEvidence, MisconceptionRecord,
    KnowledgeStatusType
)

class MasteryModel:
    """
    Explainable, bounded [0.0, 1.0] Bayesian-inspired exponential moving average
    mastery model with misconception awareness and confidence accumulation.
    """

    def __init__(
        self,
        default_alpha: float = 0.30,
        misconception_penalty: float = 0.40,
        retest_boost: float = 0.35,
        self_report_initial_mastery: float = 0.50,
        self_report_initial_confidence: float = 0.40
    ):
        self.alpha = default_alpha
        self.misconception_penalty = misconception_penalty
        self.retest_boost = retest_boost
        self.self_report_initial_mastery = self_report_initial_mastery
        self.self_report_initial_confidence = self_report_initial_confidence

    @staticmethod
    def clamp(value: float, min_val: float = 0.0, max_val: float = 1.0) -> float:
        return max(min_val, min(max_val, round(value, 3)))

    def determine_status(
        self,
        mastery_score: float,
        has_unresolved_misconception: bool,
        attempts: int
    ) -> KnowledgeStatusType:
        """
        Calculates status strictly according to Section 16 thresholds:
        - Unresolved misconception -> 'misconception'
        - 0.00 - 0.29 -> 'weak' (or 'unknown' if 0 attempts)
        - 0.30 - 0.59 -> 'learning' / 'partial'
        - 0.60 - 0.79 -> 'developing'
        - 0.80 - 1.00 -> 'mastered'
        """
        if has_unresolved_misconception:
            return "misconception"

        if attempts == 0 and mastery_score == 0.0:
            return "unknown"

        if mastery_score < 0.30:
            return "weak"
        elif mastery_score < 0.60:
            return "learning"
        elif mastery_score < 0.80:
            return "developing"
        else:
            return "mastered"

    def update_mastery(
        self,
        current_knowledge: Optional[LearnerKnowledge],
        concept_id: str,
        concept_name: str,
        evidence: LearnerEvidence
    ) -> LearnerKnowledge:
        """
        Applies deterministic update rule to concept knowledge.
        Preserves evidence log, updates attempts, confidence, and status.
        """
        now_iso = datetime.now(timezone.utc).isoformat()

        # Initialize if concept not yet tracked
        if current_knowledge is None:
            knowledge = LearnerKnowledge(
                concept_id=concept_id,
                concept_name=concept_name,
                mastery_score=0.0,
                confidence=0.0,
                status="unknown",
                attempts=0,
                correct_attempts=0,
                incorrect_attempts=0,
                misconceptions=[],
                evidence=[]
            )
        else:
            # Create a working copy
            knowledge = current_knowledge.model_copy(deep=True)

        knowledge.last_taught_at = now_iso

        # 1. SPECIAL CASE: Self-Reported Knowledge (Section 19)
        if evidence.source == "profile_self_report":
            knowledge.mastery_score = self.clamp(self.self_report_initial_mastery)
            knowledge.confidence = self.clamp(self.self_report_initial_confidence)
            knowledge.status = self.determine_status(knowledge.mastery_score, False, knowledge.attempts)
            knowledge.evidence.append(evidence)
            return knowledge

        # 2. General Evidence Processing
        knowledge.attempts += 1
        knowledge.last_assessed_at = now_iso

        old_mastery = knowledge.mastery_score
        is_misconception = bool(evidence.misconception or evidence.result == "misconception")

        # Track misconception memory (Section 17)
        unresolved_misconceptions = [m for m in knowledge.misconceptions if not m.resolved]
        had_unresolved_before = len(unresolved_misconceptions) > 0

        if is_misconception and evidence.misconception:
            # Check if this misconception was already registered
            matched = False
            for m in knowledge.misconceptions:
                if m.misconception.lower().strip() == evidence.misconception.lower().strip():
                    m.occurrences += 1
                    m.last_detected = now_iso
                    m.resolved = False
                    matched = True
                    break
            if not matched:
                knowledge.misconceptions.append(MisconceptionRecord(
                    concept_id=concept_id,
                    misconception=evidence.misconception,
                    first_detected=now_iso,
                    last_detected=now_iso,
                    occurrences=1,
                    resolved=False
                ))

        if evidence.score >= 0.7:  # Correct or high performance
            knowledge.correct_attempts += 1

            # If student previously had an unresolved misconception, this correct re-test can resolve it (Section 17 & 41)
            if had_unresolved_before:
                for m in knowledge.misconceptions:
                    if not m.resolved:
                        m.resolved = True
                        m.resolution_notes = f"Resolved via {evidence.source} with score {evidence.score}"
                # Re-test boost
                new_mastery = old_mastery * (1.0 - self.retest_boost) + evidence.score * self.retest_boost
                # Ensure it increases significantly from prior depressed state
                new_mastery = max(new_mastery, min(1.0, old_mastery + 0.25))
            elif evidence.source == "assessment":
                # Summative assessment (Section 23)
                if knowledge.attempts == 1 and old_mastery == 0.0:
                    new_mastery = evidence.score
                else:
                    new_mastery = old_mastery * 0.25 + evidence.score * 0.75
            else:
                new_mastery = old_mastery * (1.0 - self.alpha) + evidence.score * self.alpha
                # Ensure positive increment
                new_mastery = max(new_mastery, min(1.0, old_mastery + 0.10))

        elif is_misconception:
            knowledge.incorrect_attempts += 1
            # Misconception penalty is stronger than a normal mistake
            new_mastery = old_mastery * (1.0 - self.misconception_penalty) + evidence.score * self.misconception_penalty
            # Ensure negative decrement
            new_mastery = min(new_mastery, max(0.0, old_mastery - 0.15))

        else:  # Normal incorrect or partial attempt
            if evidence.source == "assessment":
                if knowledge.attempts == 1 and old_mastery == 0.0:
                    new_mastery = evidence.score
                else:
                    new_mastery = old_mastery * 0.25 + evidence.score * 0.75
            elif evidence.score < 0.3:
                knowledge.incorrect_attempts += 1
                new_mastery = old_mastery * (1.0 - self.alpha) + evidence.score * self.alpha
                # Ensure negative decrement
                new_mastery = min(new_mastery, max(0.0, old_mastery - 0.10))
            else:  # Partial
                new_mastery = old_mastery * (1.0 - (self.alpha * 0.5)) + evidence.score * (self.alpha * 0.5)

        knowledge.mastery_score = self.clamp(new_mastery)

        # 3. Confidence calculation: grows as attempts increase, dampened by inconsistency
        # 1 attempt ~ 0.45, 2 attempts ~ 0.65, 3+ attempts ~ 0.80+
        base_confidence = min(0.95, 0.30 + (0.20 * knowledge.attempts))
        knowledge.confidence = self.clamp(base_confidence * evidence.confidence)

        # 4. Status assignment
        active_misconceptions = any(not m.resolved for m in knowledge.misconceptions)
        knowledge.status = self.determine_status(
            knowledge.mastery_score,
            active_misconceptions,
            knowledge.attempts
        )

        # Record evidence
        knowledge.evidence.append(evidence)

        return knowledge


# Singleton instance
mastery_model = MasteryModel()
