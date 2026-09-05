"""
Next Topic Recommendation Engine conforming to Sections 22, 23, 56, 57.
Determines next learning milestones strictly based on provided learning paths and verified evidence.
Strictly adheres to the No-Evidence Rule: returns None if no learning path is supplied.
"""

from typing import List, Dict, Any, Optional, Tuple
from backend.assessment.models.result import WeakAreaItem


class NextTopicEngine:
    """
    Suggests the next topic in an existing learning path only if evidence supports advancement.
    Does NOT hallucinate or synthesize an unverified curriculum.
    """

    def recommend_next_topic(
        self,
        topic: str,
        strong_areas: List[str],
        weak_areas: List[WeakAreaItem],
        overall_score: float,
        learning_path: Optional[List[str]] = None
    ) -> Tuple[Optional[str], Optional[str]]:
        """
        Returns (recommended_next_topic, reasoning).
        If no learning path context is provided, returns (None, reasoning).
        """
        # 1. Prerequisite / Weak Concept Guard (Section 22)
        # If foundational understanding is weak, recommend prerequisite revision instead
        if overall_score < 0.65 or len(weak_areas) >= 2:
            return None, "Prerequisites and core concepts require revision before advancing to subsequent topics."

        # Check for foundational inverse relationship weakness in physics / circuits
        for wa in weak_areas:
            if "inverse" in wa.concept.lower() or "formula" in wa.concept.lower():
                return None, f"Foundational understanding of {wa.concept} is weak. Reinforce before advancing."

        # 2. Check for supplied learning path (Section 56 & 57)
        if not learning_path:
            # Section 56 & 57: No curriculum hallucination
            return None, "No supplied learning path or curriculum context available."

        # 3. Locate next topic in supplied path
        topic_lower = topic.strip().lower()
        normalized_path = [p.strip().lower() for p in learning_path]

        current_idx = -1
        for idx, item in enumerate(normalized_path):
            if item in topic_lower or topic_lower in item:
                current_idx = idx
                break

        if current_idx != -1 and current_idx + 1 < len(learning_path):
            next_topic = learning_path[current_idx + 1]
            return next_topic, f"Successfully mastered prerequisites for '{topic}'. Ready to advance."
        elif current_idx == -1 and len(learning_path) > 0:
            # Topic not explicitly matched; take first topic if current is introductory
            next_topic = learning_path[0]
            return next_topic, f"Advancing to curriculum milestone '{next_topic}'."

        return None, "Current learning path completed or no further topics specified."


next_topic_engine = NextTopicEngine()
