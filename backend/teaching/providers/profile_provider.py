"""
Student Profile Provider Interface conforming to Section 26.
Interfaces with Agent 3 (Student Profile Subsystem).
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class StudentProfileProvider(ABC):
    @abstractmethod
    def get_student_profile(self, student_id: str) -> Dict[str, Any]:
        pass

class PersonalizationProfileProvider(StudentProfileProvider):
    def __init__(self):
        self._fallback_profiles: Dict[str, Dict[str, Any]] = {}

    def get_student_profile(self, student_id: str) -> Dict[str, Any]:
        try:
            from backend.personalization.service import personalization_service
            profile = personalization_service.get_profile(student_id)
            if profile:
                return profile.model_dump()
        except Exception:
            pass

        if student_id in self._fallback_profiles:
            return self._fallback_profiles[student_id]
        
        # Default student profile
        return {
            "student_id": student_id,
            "educational_level": "beginner",
            "known_topics": [],
            "weak_topics": [],
            "strong_topics": [],
            "preferred_language": "English",
            "preferred_teaching_style": "analogy_based",
            "preferred_depth": "standard"
        }

    def set_student_profile(self, student_id: str, profile: Dict[str, Any]):
        self._fallback_profiles[student_id] = profile
        try:
            from backend.personalization.service import personalization_service
            from backend.personalization.schemas import CreateProfileRequest
            personalization_service.create_or_update_profile(CreateProfileRequest(
                student_id=student_id,
                educational_level=profile.get("educational_level", "beginner"),
                preferred_language=profile.get("preferred_language", "English"),
                preferred_teaching_style=profile.get("preferred_teaching_style", "analogy_based"),
                preferred_depth=profile.get("preferred_depth", "standard"),
                known_concepts=profile.get("known_topics", []) or profile.get("known_concepts", [])
            ))
        except Exception:
            pass

# InMemoryProfileProvider alias for backwards compatibility
InMemoryProfileProvider = PersonalizationProfileProvider
student_profile_provider = PersonalizationProfileProvider()
