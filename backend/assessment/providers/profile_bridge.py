"""
Agent 3 Learner Profile Bridge conforming to Sections 26, 28, 60.
Emits assessment evidence to Agent 3 (Personalization Subsystem)
and consumes historical mastery for explainable progress calculations.
Strictly does NOT maintain a duplicate learner database.
"""

import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class ProfileBridge:
    """
    Subsystem interface connecting Agent 7 to Agent 3.
    Updates learner mastery state and fetches historical progress evidence.
    """

    def __init__(self, service=None):
        self._service = service

    def get_service(self):
        if self._service is not None:
            return self._service
        try:
            from backend.personalization.service import personalization_service
            return personalization_service
        except Exception as e:
            logger.warning(f"Could not load personalization_service: {e}")
            return None

    def emit_assessment_evidence(
        self,
        student_id: str,
        assessment_id: str,
        lesson_id: Optional[str],
        topic: str,
        score: float,
        concept_scores: Dict[str, float],
        weak_concepts: List[str],
        strong_concepts: List[str],
        misconceptions: List[str]
    ) -> bool:
        """
        Sends structured assessment outcome to Agent 3.
        Agent 3 uses this to update concept mastery, learning history, and active misconceptions.
        """
        service = self.get_service()
        if not service:
            logger.warning(f"PersonalizationService unavailable. Evidence for student {student_id} not persisted.")
            return False

        try:
            evidence_data = {
                "assessment_id": assessment_id,
                "lesson_id": lesson_id or "",
                "topic": topic,
                "score": score,
                "concept_scores": concept_scores,
                "weak_concepts": weak_concepts,
                "strong_concepts": strong_concepts,
                "misconceptions": misconceptions,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            service.record_assessment_result(student_id, evidence_data)
            logger.info(f"Successfully recorded assessment result in Agent 3 for student '{student_id}'.")
            return True
        except Exception as e:
            logger.error(f"Failed to record assessment result in Agent 3: {e}")
            return False

    def get_student_mastery_context(self, student_id: str, topic: Optional[str] = None) -> Dict[str, Any]:
        """
        Queries Agent 3 for existing concept mastery levels and learning path.
        Used to calculate historical blended progress and recommend next topics.
        """
        service = self.get_service()
        if not service:
            return {}

        try:
            profile = service.repository.get_profile(student_id)
            if not profile:
                return {}

            mastery_dict = {
                c_id: k.mastery_score
                for c_id, k in profile.concept_mastery.items()
            }
            
            # Extract current learning path if available
            learning_path = []
            if profile.current_learning_path and profile.current_learning_path.nodes:
                learning_path = [node.concept for node in profile.current_learning_path.nodes]

            return {
                "concept_mastery": mastery_dict,
                "known_concepts": profile.known_concepts,
                "learning_path": learning_path,
                "educational_level": profile.educational_level
            }
        except Exception as e:
            logger.warning(f"Could not retrieve student mastery context: {e}")
            return {}


profile_bridge = ProfileBridge()
