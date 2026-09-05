"""
Shared Data Contracts for AI Teacher
Strictly adheres to Section 6 of the Master Project Context:
- StudentProfile (6.1)
- LearningRequest (6.2)
- LessonPlan (6.3)
- TeachingStep (6.4)
- StudentResponse (6.5)
- EvaluationResult (6.6)
- LearningReport (6.7)
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime, timezone
import uuid


class StudentProfile(BaseModel):
    student_id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    educational_level: str = "beginner"  # beginner, intermediate, advanced, high_school, undergraduate
    known_topics: List[str] = Field(default_factory=list)
    weak_topics: List[str] = Field(default_factory=list)
    strong_topics: List[str] = Field(default_factory=list)
    learning_objectives: List[str] = Field(default_factory=list)
    preferred_language: str = "English"  # English, Hindi, Hinglish
    preferred_teaching_style: str = "interactive"  # interactive, analogy_driven, visual, rigorous
    preferred_depth: str = "intuitive"  # intuitive, standard, deep_dive
    current_learning_path: List[str] = Field(default_factory=list)
    assessment_history: List[Dict[str, Any]] = Field(default_factory=list)
    learning_history: List[Dict[str, Any]] = Field(default_factory=list)


class LearningRequest(BaseModel):
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    student_id: str
    topic: Optional[str] = None
    material_id: Optional[str] = None
    educational_level: str = "beginner"
    existing_knowledge: str = "None"
    learning_objective: str = "Understand foundational principles and apply them"
    preferred_language: str = "Hinglish"  # English, Hindi, Hinglish
    teaching_style: str = "analogy_driven"
    available_time: int = 20  # minutes
    available_time_minutes: Optional[int] = None
    desired_depth: str = "intuitive"

    def model_post_init(self, __context: Any) -> None:
        if self.available_time_minutes is not None and self.available_time == 20:
            self.available_time = self.available_time_minutes
        elif self.available_time_minutes is None:
            self.available_time_minutes = self.available_time


class LessonPlan(BaseModel):
    lesson_id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    topic: str
    learning_objectives: List[str] = Field(default_factory=list)
    prerequisites: List[str] = Field(default_factory=list)
    ordered_concepts: List[str] = Field(default_factory=list)
    concept_dependencies: Dict[str, List[str]] = Field(default_factory=dict)
    estimated_duration: int = 20  # minutes
    explanation_strategy: str = "Step-by-step conceptual grounding with visual demonstration and interactive check"
    examples: List[Dict[str, Any]] = Field(default_factory=list)
    visual_requirements: List[Dict[str, Any]] = Field(default_factory=list)
    question_points: List[str] = Field(default_factory=list)
    assessment_strategy: str = "Formative concept probes during lesson + Summative 3-question mastery check"
    adaptation_rules: List[Dict[str, Any]] = Field(default_factory=list)


class VisualInstruction(BaseModel):
    type: str  # circuit, math_derivation, code_trace, diagram, concept_map
    title: str
    data: Dict[str, Any] = Field(default_factory=dict)
    caption: str = ""


class QuestionPayload(BaseModel):
    question_id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    prompt: str
    expected_answer: str = ""
    options: Optional[List[str]] = None
    hints: List[str] = Field(default_factory=list)
    question_type: str = "conceptual_check"  # conceptual_check, diagnostic, follow_up, assessment
    pedagogical_goal: str = ""


class TeachingStep(BaseModel):
    step_id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    lesson_id: str
    concept_id: str
    step_type: str  # introduction, explanation, example, demonstration, visual, question, assessment, re_explanation, summary
    objective: str
    explanation: str
    example: Optional[str] = None
    visual_instruction: Optional[VisualInstruction] = None
    language: str = "Hinglish"
    difficulty: str = "beginner"
    question: Optional[QuestionPayload] = None
    expected_understanding: str = ""
    source_references: List[Dict[str, Any]] = Field(default_factory=list)
    avatar_emotion: str = "explaining"  # explaining, encouraging, thoughtful, celebrating, attentive
    video_asset: Optional[Dict[str, Any]] = None  # Composed video scene (Agent 4)
    audio_asset: Optional[Dict[str, Any]] = None  # Synthesized voice narration (Agent 5)
    avatar_asset: Optional[Dict[str, Any]] = None  # Teacher avatar state/video (Agent 5)


class StudentResponse(BaseModel):
    session_id: str
    question_id: str
    student_answer: str
    answer_type: str = "text"  # text, voice, option
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class EvaluationResult(BaseModel):
    correctness: bool
    confidence: float = 1.0
    concept: str
    misconception: Optional[str] = None
    knowledge_gap: Optional[str] = None
    reasoning_quality: str = "Satisfactory"
    recommended_action: str  # continue, simplify, re_explain, give_analogy, ask_followup, reduce_difficulty, increase_difficulty, revisit_prerequisite, move_to_next_concept
    teacher_thought: str = ""  # pedagogical rationale for the adaptive decision
    bloom_level: str = "Understanding"


class LearningReport(BaseModel):
    lesson_id: str
    score: float = 0.0  # percentage (0.0 to 100.0)
    concepts_understood: List[str] = Field(default_factory=list)
    weak_areas: List[str] = Field(default_factory=list)
    misconceptions: List[str] = Field(default_factory=list)
    concepts_requiring_revision: List[str] = Field(default_factory=list)
    recommended_practice: List[str] = Field(default_factory=list)
    recommended_next_topic: str = ""
    overall_progress: str = "Completed initial learning loop with adaptive mastery"
    completed_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class SessionState(BaseModel):
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    correlation_id: str = Field(default_factory=lambda: f"corr_{uuid.uuid4().hex[:8]}")
    student_profile: StudentProfile
    learning_request: LearningRequest
    lesson_plan: Optional[LessonPlan] = None
    current_step_index: int = 0
    steps: List[TeachingStep] = Field(default_factory=list)
    current_concept: str = ""
    status: str = "initialized"  # initialized, planning, teaching, questioning, evaluating, adapting, assessment, completed
    history: List[Dict[str, Any]] = Field(default_factory=list)
    evaluations: List[EvaluationResult] = Field(default_factory=list)
    learning_report: Optional[LearningReport] = None
    active_misconception: Optional[str] = None
    adaptation_count: int = 0
    reteach_attempts_by_concept: Dict[str, int] = Field(default_factory=dict)
