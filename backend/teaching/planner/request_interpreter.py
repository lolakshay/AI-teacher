"""
Request Interpreter Subsystem conforming to Section 8.
Normalizes conflicting user preferences and builds a canonical TeachingIntent.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from backend.teaching.schemas.learning_request import LearningRequest
import logging

logger = logging.getLogger(__name__)

class TeachingIntent(BaseModel):
    topic: str
    material_id: Optional[str] = None
    learner_level: str = "beginner"
    learning_goal: str = ""
    language: str = "English"
    available_minutes: float = 20.0
    depth: str = "standard"
    known_concepts: List[str] = Field(default_factory=list)
    likely_prerequisites: List[str] = Field(default_factory=list)
    teaching_style: str = "analogy_based"
    interaction_frequency: str = "medium"
    estimated_complexity: float = 0.5


class RequestInterpreter:
    def interpret(
        self,
        request: LearningRequest,
        student_profile: Optional[Dict[str, Any]] = None
    ) -> TeachingIntent:
        profile = student_profile or {}
        
        # Determine topic name
        topic = (request.topic or "").strip()
        if not topic and request.material_id:
            topic = "Uploaded Material Analysis"

        # Resolve learner level: prioritize explicit request or fallback to profile
        learner_level = request.educational_level or profile.get("educational_level", "beginner")

        # Resolve language
        language = request.preferred_language or profile.get("preferred_language", "English")

        # Available time
        available_time = float(request.available_time_minutes) if request.available_time_minutes > 0 else 20.0

        # Normalization rule for contradictory requests (e.g. 5 min vs deep):
        # Time constraint takes high priority. If time <= 10 min, depth MUST be compressed.
        depth = request.desired_depth
        if available_time <= 7.0 and depth in ["deep", "exhaustive"]:
            logger.info("Compressed depth from '%s' to 'quick' due to tight time limit (%.1f mins)", depth, available_time)
            depth = "quick"
        elif available_time <= 15.0 and depth == "exhaustive":
            depth = "standard"

        # Known knowledge
        known_concepts = list(request.existing_knowledge)
        for t in profile.get("known_topics", []):
            if t not in known_concepts:
                known_concepts.append(t)

        # Style & frequency
        style = request.teaching_style or profile.get("preferred_teaching_style", "analogy_based")
        frequency = "high" if available_time <= 10.0 or style in ["exam_focused", "practical"] else "medium"

        # Complexity estimation & likely prerequisites
        topic_lower = topic.lower()
        if "ohm" in topic_lower or "circuit" in topic_lower:
            prereqs = ["electric charge", "potential difference", "elementary algebra"]
            complexity = 0.4
        elif "binary search" in topic_lower or "algorithm" in topic_lower:
            prereqs = ["sorted array indexing", "divide and conquer"]
            complexity = 0.5
        elif "newton" in topic_lower or "force" in topic_lower:
            prereqs = ["mass and acceleration", "vectors intuition"]
            complexity = 0.4
        else:
            prereqs = ["foundational domain terminology"]
            complexity = 0.5

        # Refine complexity by learner level
        if learner_level == "advanced":
            complexity = min(1.0, complexity + 0.2)
        elif learner_level == "beginner":
            complexity = max(0.1, complexity - 0.1)

        return TeachingIntent(
            topic=topic,
            material_id=request.material_id,
            learner_level=learner_level,
            learning_goal=request.learning_objective,
            language=language,
            available_minutes=available_time,
            depth=depth,
            known_concepts=known_concepts,
            likely_prerequisites=prereqs,
            teaching_style=style,
            interaction_frequency=frequency,
            estimated_complexity=complexity
        )

request_interpreter = RequestInterpreter()
