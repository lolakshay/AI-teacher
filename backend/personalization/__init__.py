"""
Personalization Subsystem (Agent 3) Package.
Core exports:
- PersonalizationService
- personalization_service (singleton)
- PersonalizationEngine
- personalization_engine (singleton)
- MasteryModel
- mastery_model (singleton)
- SQLiteProfileRepository
- InMemoryProfileRepository
- profile_repository (singleton)
- All schema models
"""

from backend.personalization.schemas import (
    StudentProfile, StudentPreferences, LearnerKnowledge,
    MisconceptionRecord, LearnerEvidence, LearningHistoryEntry,
    AssessmentHistoryEntry, CurrentLearningPath, PathNode,
    PersonalizationContext, CreateProfileRequest, UpdateProfileRequest,
    KnowledgeUpdateEvidence, ResetProfileRequest
)

from backend.personalization.mastery_model import MasteryModel, mastery_model
from backend.personalization.engine import PersonalizationEngine, personalization_engine
from backend.personalization.repository import (
    StudentProfileRepository, SQLiteProfileRepository,
    InMemoryProfileRepository, profile_repository
)
from backend.personalization.service import PersonalizationService, personalization_service

__all__ = [
    "StudentProfile",
    "StudentPreferences",
    "LearnerKnowledge",
    "MisconceptionRecord",
    "LearnerEvidence",
    "LearningHistoryEntry",
    "AssessmentHistoryEntry",
    "CurrentLearningPath",
    "PathNode",
    "PersonalizationContext",
    "CreateProfileRequest",
    "UpdateProfileRequest",
    "KnowledgeUpdateEvidence",
    "ResetProfileRequest",
    "MasteryModel",
    "mastery_model",
    "PersonalizationEngine",
    "personalization_engine",
    "StudentProfileRepository",
    "SQLiteProfileRepository",
    "InMemoryProfileRepository",
    "profile_repository",
    "PersonalizationService",
    "personalization_service",
]
