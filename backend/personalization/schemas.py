"""
Personalization and Learner Model Schemas conforming to Part 3 specifications.
Defines strongly typed contracts for:
- StudentPreferences
- MisconceptionRecord
- LearnerEvidence
- LearnerKnowledge (Concept Mastery)
- LearningHistoryEntry
- AssessmentHistoryEntry
- CurrentLearningPath
- StudentProfile
- PersonalizationContext
"""

from typing import List, Dict, Any, Optional, Literal
from pydantic import BaseModel, Field
from datetime import datetime, timezone
import uuid

# ----------------- LITERAL TYPES -----------------

TeachingStyleType = Literal[
    "simple",
    "analogy_based",
    "conceptual",
    "practical",
    "exam_focused",
    "technical",
    "custom"
]

DepthType = Literal["quick", "standard", "deep", "exhaustive"]
InteractionFrequencyType = Literal["low", "medium", "high"]
ExamplePreferenceType = Literal["real_world", "academic", "technical", "mixed"]
ExplanationPreferenceType = Literal["visual", "verbal", "step_by_step", "mixed"]

KnowledgeStatusType = Literal[
    "unknown",
    "learning",
    "partial",
    "developing",
    "mastered",
    "weak",
    "misconception"
]

EvidenceSourceType = Literal[
    "lesson_response",
    "profile_self_report",
    "assessment",
    "teacher_evaluation",
    "practice_problem"
]

# ----------------- PREFERENCES (LAYER 1) -----------------

class StudentPreferences(BaseModel):
    preferred_language: str = "English"
    preferred_teaching_style: TeachingStyleType = "analogy_based"
    preferred_depth: DepthType = "standard"
    interaction_frequency: InteractionFrequencyType = "medium"
    example_preference: ExamplePreferenceType = "real_world"
    explanation_preference: ExplanationPreferenceType = "mixed"
    typical_session_duration_minutes: Optional[int] = 20

# ----------------- MISCONCEPTIONS & EVIDENCE -----------------

class MisconceptionRecord(BaseModel):
    concept_id: str
    misconception: str
    first_detected: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    last_detected: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    occurrences: int = 1
    resolved: bool = False
    resolution_notes: Optional[str] = None

class LearnerEvidence(BaseModel):
    source: EvidenceSourceType
    session_id: Optional[str] = None
    question_id: Optional[str] = None
    result: str = "evaluated"  # correct, incorrect, partial, misconception, self_reported
    score: float = Field(default=0.0, ge=0.0, le=1.0)
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    misconception: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    details: Dict[str, Any] = Field(default_factory=dict)

# ----------------- LEARNED KNOWLEDGE (LAYER 3) -----------------

class LearnerKnowledge(BaseModel):
    concept_id: str
    concept_name: str
    mastery_score: float = Field(default=0.0, ge=0.0, le=1.0)
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    status: KnowledgeStatusType = "unknown"
    attempts: int = 0
    correct_attempts: int = 0
    incorrect_attempts: int = 0
    last_assessed_at: Optional[str] = None
    last_taught_at: Optional[str] = None
    misconceptions: List[MisconceptionRecord] = Field(default_factory=list)
    evidence: List[LearnerEvidence] = Field(default_factory=list)

# ----------------- LEARNING HISTORY (LAYER 4) -----------------

class LearningHistoryEntry(BaseModel):
    session_id: str
    lesson_id: str
    topic: str
    started_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    completed_at: Optional[str] = None
    duration_minutes: float = 0.0
    concepts_covered: List[str] = Field(default_factory=list)
    concepts_mastered: List[str] = Field(default_factory=list)
    concepts_struggled: List[str] = Field(default_factory=list)
    assessment_score: Optional[float] = None

class AssessmentHistoryEntry(BaseModel):
    assessment_id: str
    lesson_id: str
    topic: str
    score: float = Field(default=0.0, ge=0.0, le=1.0)
    concept_scores: Dict[str, float] = Field(default_factory=dict)
    weak_concepts: List[str] = Field(default_factory=list)
    strong_concepts: List[str] = Field(default_factory=list)
    misconceptions: List[str] = Field(default_factory=list)
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

# ----------------- LEARNING PATH (LAYER 5) -----------------

class PathNode(BaseModel):
    concept: str
    status: Literal["not_started", "learning", "mastered"] = "not_started"

class CurrentLearningPath(BaseModel):
    path_id: str
    title: str
    nodes: List[PathNode] = Field(default_factory=list)
    current_node: str = ""

# ----------------- FULL STUDENT PROFILE (AGGREGATE) -----------------

class StudentProfile(BaseModel):
    student_id: str
    educational_level: str = "beginner"  # beginner, intermediate, advanced, custom
    preferred_language: str = "English"
    preferred_teaching_style: TeachingStyleType = "analogy_based"
    preferred_depth: DepthType = "standard"

    learning_objectives: List[str] = Field(default_factory=list)
    known_concepts: List[str] = Field(default_factory=list)
    strong_concepts: List[str] = Field(default_factory=list)
    weak_concepts: List[str] = Field(default_factory=list)
    misconceptions: List[MisconceptionRecord] = Field(default_factory=list)

    current_learning_path: Optional[CurrentLearningPath] = None
    learning_history: List[LearningHistoryEntry] = Field(default_factory=list)
    assessment_history: List[AssessmentHistoryEntry] = Field(default_factory=list)
    concept_mastery: Dict[str, LearnerKnowledge] = Field(default_factory=dict)

    preferences: StudentPreferences = Field(default_factory=StudentPreferences)
    inferred_preferences: Dict[str, Any] = Field(default_factory=dict)

    profile_schema_version: int = 1
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

# ----------------- ACTIONABLE PERSONALIZATION CONTEXT -----------------

class PersonalizationContext(BaseModel):
    student_id: str
    learner_level: str
    preferred_language: str
    teaching_style: str
    preferred_depth: str
    interaction_frequency: str
    available_time_minutes: float = 20.0

    known_concepts: List[str] = Field(default_factory=list)
    strong_concepts: List[str] = Field(default_factory=list)
    weak_concepts: List[str] = Field(default_factory=list)
    misconceptions: List[str] = Field(default_factory=list)

    topic_mastery: Dict[str, float] = Field(default_factory=dict)
    relevant_prior_learning: List[str] = Field(default_factory=list)
    recommended_prerequisites: List[str] = Field(default_factory=list)
    recent_performance: Dict[str, Any] = Field(default_factory=dict)

    recommended_focus: List[str] = Field(default_factory=list)
    avoid_assuming: List[str] = Field(default_factory=list)

    # Actionable pedagogical constraints consumed by Agent 1
    explanation_constraints: List[str] = Field(default_factory=list)
    question_constraints: List[str] = Field(default_factory=list)

    # Transparent explainable decision reasons
    reasoning: List[str] = Field(default_factory=list)

# ----------------- DTOs & API PAYLOADS -----------------

class CreateProfileRequest(BaseModel):
    student_id: str
    educational_level: Optional[str] = "beginner"
    preferred_language: Optional[str] = "English"
    preferred_teaching_style: Optional[TeachingStyleType] = "analogy_based"
    preferred_depth: Optional[DepthType] = "standard"
    learning_objectives: Optional[List[str]] = None
    known_concepts: Optional[List[str]] = None
    preferences: Optional[Dict[str, Any]] = None

class UpdateProfileRequest(BaseModel):
    educational_level: Optional[str] = None
    preferred_language: Optional[str] = None
    preferred_teaching_style: Optional[TeachingStyleType] = None
    preferred_depth: Optional[DepthType] = None
    learning_objectives: Optional[List[str]] = None
    known_concepts: Optional[List[str]] = None
    preferences: Optional[Dict[str, Any]] = None
    current_learning_path: Optional[CurrentLearningPath] = None

class KnowledgeUpdateEvidence(BaseModel):
    source: EvidenceSourceType = "lesson_response"
    session_id: Optional[str] = None
    question_id: Optional[str] = None
    correctness: float = Field(..., ge=0.0, le=1.0)
    classification: Optional[str] = None
    misconception: Optional[str] = None
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    details: Dict[str, Any] = Field(default_factory=dict)

class ResetProfileRequest(BaseModel):
    reset_type: Literal[
        "RESET_PREFERENCES",
        "RESET_KNOWLEDGE",
        "RESET_HISTORY",
        "RESET_ALL"
    ]
