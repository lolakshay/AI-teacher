"""
Deterministic Personalization Engine conforming to Sections 11-13, 27-34, 43-44.
Combines student profile, current session request, and topic knowledge to generate
compact, highly actionable PersonalizationContext for Agent 1 (Teaching Brain).
"""

from typing import Optional, List, Dict, Any, Set
from backend.personalization.schemas import (
    StudentProfile, PersonalizationContext, LearnerKnowledge
)

class PersonalizationEngine:
    """
    Evaluates profile preferences, verified concept mastery, and current session parameters
    using a deterministic 5-tier priority resolution model.
    """

    # Domain associations for topic-specific filtering
    TOPIC_CONCEPT_MAPPINGS: Dict[str, List[str]] = {
        "ohm": ["voltage", "current", "resistance", "ohms_law", "conductance", "circuits"],
        "circuit": ["voltage", "current", "resistance", "ohms_law", "kirchhoffs_laws", "series_parallel", "capacitance"],
        "electricity": ["charge", "voltage", "current", "resistance", "power", "electric_field"],
        "machine learning": ["python", "linear_algebra", "calculus", "supervised_learning", "gradient_descent", "neural_networks"],
        "python": ["variables", "loops", "functions", "oop", "data_structures"]
    }

    # Known prerequisite relations
    PREREQUISITE_GRAPH: Dict[str, List[str]] = {
        "ohms_law": ["voltage", "current", "resistance"],
        "kirchhoffs_laws": ["ohms_law", "series_parallel"],
        "power": ["voltage", "current"],
        "supervised_learning": ["python", "linear_algebra"]
    }

    def generate_context(
        self,
        profile: StudentProfile,
        topic: Optional[str] = None,
        current_request: Optional[Any] = None
    ) -> PersonalizationContext:
        """
        Produces an actionable PersonalizationContext strictly following priority:
        1. Explicit Current Request
        2. Explicit Profile Preferences
        3. Verified Concept Mastery & Misconceptions
        4. Inferred Preferences
        5. System Defaults
        """
        reasoning: List[str] = []

        # --- 1. RESOLVE LEVEL (Priority 1 > Priority 2 > Default) ---
        req_level = getattr(current_request, "educational_level", None)
        if req_level and req_level.strip():
            level = req_level.lower().strip()
            reasoning.append(f"Educational level set to '{level}' from explicit session request.")
        elif profile.educational_level:
            level = profile.educational_level.lower().strip()
            reasoning.append(f"Educational level set to '{level}' from student profile default.")
        else:
            level = "beginner"
            reasoning.append("Educational level defaulted to 'beginner'.")

        # --- 2. RESOLVE LANGUAGE ---
        req_lang = getattr(current_request, "preferred_language", None)
        if req_lang and req_lang.strip():
            language = req_lang.strip()
            reasoning.append(f"Instruction language set to '{language}' per current session request override.")
        elif profile.preferences.preferred_language:
            language = profile.preferences.preferred_language
            reasoning.append(f"Instruction language set to '{language}' from profile preferences.")
        elif profile.preferred_language:
            language = profile.preferred_language
            reasoning.append(f"Instruction language set to '{language}' from profile.")
        else:
            language = "English"

        # --- 3. RESOLVE TEACHING STYLE ---
        req_style = getattr(current_request, "teaching_style", None)
        if req_style and req_style.strip():
            style = req_style.strip()
            reasoning.append(f"Teaching style set to '{style}' from session request override.")
        elif profile.preferences.preferred_teaching_style:
            style = profile.preferences.preferred_teaching_style
            reasoning.append(f"Teaching style set to '{style}' from student preferences.")
        elif profile.preferred_teaching_style:
            style = profile.preferred_teaching_style
            reasoning.append(f"Teaching style set to '{style}' from profile.")
        else:
            style = "analogy_based"

        # --- 4. RESOLVE DEPTH ---
        req_depth = getattr(current_request, "desired_depth", None)
        if req_depth and req_depth.strip():
            depth = req_depth.strip()
            reasoning.append(f"Lesson depth set to '{depth}' from session request.")
        elif profile.preferences.preferred_depth:
            depth = profile.preferences.preferred_depth
            reasoning.append(f"Lesson depth set to '{depth}' from profile preferences.")
        elif profile.preferred_depth:
            depth = profile.preferred_depth
            reasoning.append(f"Lesson depth set to '{depth}' from profile.")
        else:
            depth = "standard"

        # --- 5. RESOLVE DURATION ---
        req_time = getattr(current_request, "available_time_minutes", None)
        if req_time is None:
            req_time = getattr(current_request, "available_time", None)

        if req_time is not None and float(req_time) > 0:
            duration = float(req_time)
            reasoning.append(f"Available session time set to {duration:.0f} minutes from session request.")
        elif profile.preferences.typical_session_duration_minutes:
            duration = float(profile.preferences.typical_session_duration_minutes)
            reasoning.append(f"Available session time set to {duration:.0f} minutes from profile typical duration.")
        else:
            duration = 20.0

        # --- 6. INTERACTION FREQUENCY ---
        interaction_freq = profile.preferences.interaction_frequency or "medium"

        # --- 7. TOPIC-SPECIFIC FILTERING & KNOWLEDGE ANALYSIS (Sections 11 & 12) ---
        target_topic = topic or getattr(current_request, "topic", None) or ""
        relevant_concepts = self._get_relevant_concept_ids(target_topic)

        known_concepts: List[str] = []
        strong_concepts: List[str] = []
        weak_concepts: List[str] = []
        active_misconceptions: List[str] = []
        topic_mastery: Dict[str, float] = {}
        recommended_prerequisites: List[str] = []
        recommended_focus: List[str] = []
        avoid_assuming: List[str] = []

        # Categorize concepts from profile.concept_mastery
        for c_id, k in profile.concept_mastery.items():
            # If target topic specified, only include relevant concepts
            if relevant_concepts and not self._is_concept_relevant(c_id, relevant_concepts):
                continue

            topic_mastery[c_id] = k.mastery_score

            # Check misconceptions
            for m in k.misconceptions:
                if not m.resolved:
                    active_misconceptions.append(f"{c_id}: {m.misconception}")
                    reasoning.append(f"Active misconception detected in '{c_id}': '{m.misconception}'. Requires remediation.")

            if k.status == "mastered" or k.mastery_score >= 0.80:
                strong_concepts.append(c_id)
                known_concepts.append(c_id)
            elif k.status in ("learning", "developing", "partial") or (0.30 <= k.mastery_score < 0.80):
                known_concepts.append(c_id)
            elif k.status in ("weak", "misconception") or k.mastery_score < 0.30:
                weak_concepts.append(c_id)
                recommended_focus.append(c_id)
                reasoning.append(f"Concept '{c_id}' flagged for reinforcement due to weak mastery ({k.mastery_score:.2f}).")

        # Also incorporate static profile lists if concept_mastery did not already cover them
        for c in profile.known_concepts:
            if c not in known_concepts:
                known_concepts.append(c)
        for c in profile.strong_concepts:
            if c not in strong_concepts:
                strong_concepts.append(c)
        for c in profile.weak_concepts:
            if c not in weak_concepts:
                weak_concepts.append(c)
                if c not in recommended_focus:
                    recommended_focus.append(c)

        for m in profile.misconceptions:
            if isinstance(m, dict):
                if not m.get("resolved", False):
                    active_misconceptions.append(f"{m.get('concept_id', '')}: {m.get('misconception', '')}")
            elif hasattr(m, "resolved") and not m.resolved:
                active_misconceptions.append(f"{m.concept_id}: {m.misconception}")

        # Check prerequisite status for the topic
        for key, prereqs in self.PREREQUISITE_GRAPH.items():
            if target_topic and key in target_topic.lower().replace(" ", "_"):
                for p in prereqs:
                    p_score = topic_mastery.get(p, 0.0)
                    if p_score < 0.60:
                        recommended_prerequisites.append(p)
                        avoid_assuming.append(f"Deep mastery of {p}")

        # Recent performance summary from history
        recent_performance = self._summarize_recent_performance(profile)

        # --- 8. GENERATE ACTIONABLE PEDAGOGICAL CONSTRAINTS (Sections 13 & 34) ---
        explanation_constraints: List[str] = []
        question_constraints: List[str] = []

        if level == "beginner":
            explanation_constraints.append("Define all domain-specific terminology before introducing formal definitions.")
            explanation_constraints.append("Anchor core concepts using tangible everyday real-world analogies.")
            explanation_constraints.append("Avoid heavy mathematical formalisms initially; build intuition first.")
            explanation_constraints.append("Proceed step-by-step with zero skipped logical stages.")
            question_constraints.append("Begin with qualitative conceptual checks before any numerical tasks.")
            question_constraints.append("Provide scaffolded hints if the student hesitates or struggles.")
            avoid_assuming.append("Advanced background theory or complex formulas.")
        elif level == "intermediate":
            explanation_constraints.append("Employ standard technical vocabulary alongside clear physical interpretations.")
            explanation_constraints.append("Utilize practical application examples and schematic demonstrations.")
            explanation_constraints.append("Highlight standard formulas and explain the relationships between variables.")
            question_constraints.append("Combine conceptual diagnostic questions with direct application problems.")
            question_constraints.append("Probe causal connections between interdependent variables.")
        else:  # advanced / custom
            explanation_constraints.append("Adopt precise technical terminology and rigorous mathematical formulation.")
            explanation_constraints.append("Explore boundary conditions, edge cases, and non-ideal system behaviors.")
            explanation_constraints.append("Focus on theoretical depth and underlying physical/computational derivations.")
            question_constraints.append("Challenge student with analytical multi-step problems and edge cases.")
            question_constraints.append("Test deep mechanistic reasoning rather than surface recall.")

        # Style-specific constraints
        if style == "analogy_based" or style == "simple":
            explanation_constraints.append("Use a memorable central physical analogy (e.g., water pipe for electric circuits).")
        elif style == "practical":
            explanation_constraints.append("Ground principles in real-world engineering or troubleshooting scenarios.")
        elif style == "exam_focused":
            explanation_constraints.append("Emphasize standard exam problem patterns, pitfalls, and scoring criteria.")

        # Misconception remediation constraint
        if active_misconceptions:
            explanation_constraints.append(
                f"Address known misconception directly with counter-intuitive demonstration: {active_misconceptions[0]}"
            )
            avoid_assuming.append(f"Correct intuition regarding: {active_misconceptions[0]}")

        # Pacing / Time constraints
        if duration <= 10:
            explanation_constraints.append("Time is constrained: keep explanations concise and focus strictly on primary rule.")
        elif duration >= 30:
            explanation_constraints.append("Ample time available: include exploratory details and deep question probes.")

        # Interaction frequency constraint
        if interaction_freq == "high":
            question_constraints.append("Perform an active understanding check after each individual sub-concept.")
        elif interaction_freq == "low":
            question_constraints.append("Reserve questions for major section milestones.")
        else:
            question_constraints.append("Pose formative check questions every 2-3 conceptual steps.")

        return PersonalizationContext(
            student_id=profile.student_id,
            learner_level=level,
            preferred_language=language,
            teaching_style=style,
            preferred_depth=depth,
            interaction_frequency=interaction_freq,
            available_time_minutes=duration,
            known_concepts=known_concepts,
            strong_concepts=strong_concepts,
            weak_concepts=weak_concepts,
            misconceptions=active_misconceptions,
            topic_mastery=topic_mastery,
            relevant_prior_learning=[k for k in known_concepts if k not in weak_concepts],
            recommended_prerequisites=recommended_prerequisites,
            recent_performance=recent_performance,
            recommended_focus=recommended_focus,
            avoid_assuming=avoid_assuming,
            explanation_constraints=explanation_constraints,
            question_constraints=question_constraints,
            reasoning=reasoning
        )

    def _get_relevant_concept_ids(self, topic: str) -> Set[str]:
        if not topic:
            return set()
        topic_lower = topic.lower()
        matched: Set[str] = set()
        for key, concepts in self.TOPIC_CONCEPT_MAPPINGS.items():
            if key in topic_lower:
                matched.update(concepts)
        return matched

    def _is_concept_relevant(self, concept_id: str, relevant_set: Set[str]) -> bool:
        c_norm = concept_id.lower().replace(" ", "_").replace("-", "_")
        for r in relevant_set:
            if r in c_norm or c_norm in r:
                return True
        return False

    def _summarize_recent_performance(self, profile: StudentProfile) -> Dict[str, Any]:
        if not profile.assessment_history and not profile.learning_history:
            return {"average_score": None, "completed_lessons": 0}

        scores = [a.score for a in profile.assessment_history if a.score is not None]
        for l in profile.learning_history:
            if l.assessment_score is not None:
                scores.append(l.assessment_score)

        avg_score = (sum(scores) / len(scores)) if scores else None
        return {
            "average_score": round(avg_score, 2) if avg_score is not None else None,
            "completed_lessons": len(profile.learning_history),
            "assessments_taken": len(profile.assessment_history)
        }


# Singleton instance
personalization_engine = PersonalizationEngine()
