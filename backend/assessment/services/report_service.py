"""
Learning Report Service conforming to Sections 24, 25, 40, 41, 42, 55.
Compiles the comprehensive, evidence-grounded LearningReport.
Produces cautious, specific, and explainable human-readable feedback.
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone

from backend.assessment.models.report import LearningReport, RevisionRecommendation
from backend.assessment.models.result import (
    ScoreSummary, ConceptResult, WeakAreaItem, AggregatedMisconception, QuestionResult
)
from backend.assessment.providers.profile_bridge import profile_bridge, ProfileBridge
from backend.assessment.recommendations.revision import revision_engine, RevisionEngine
from backend.assessment.recommendations.next_topic import next_topic_engine, NextTopicEngine
from backend.app.services.llm_service import llm_service

logger = logging.getLogger(__name__)


class ReportService:
    """
    Assembles final diagnostic learning reports for learners and downstream agents.
    """

    def __init__(
        self,
        p_bridge: Optional[ProfileBridge] = None,
        rev_engine: Optional[RevisionEngine] = None,
        nxt_engine: Optional[NextTopicEngine] = None
    ):
        self.profile_bridge = p_bridge or profile_bridge
        self.revision_engine = rev_engine or revision_engine
        self.next_topic_engine = nxt_engine or next_topic_engine

    def compile_report(
        self,
        assessment_id: str,
        student_id: str,
        lesson_id: Optional[str],
        topic: str,
        score: ScoreSummary,
        question_results: List[QuestionResult],
        concept_results: List[ConceptResult],
        weak_areas: List[WeakAreaItem],
        strong_areas: List[str],
        misconceptions: List[AggregatedMisconception],
        learning_path: Optional[List[str]] = None
    ) -> LearningReport:
        """
        Builds the complete LearningReport contract.
        """
        # 1. Fetch student context from Agent 3 for historical mastery & learning path
        mastery_context = self.profile_bridge.get_student_mastery_context(student_id, topic)
        if not learning_path and mastery_context.get("learning_path"):
            learning_path = mastery_context["learning_path"]

        # 2. Compute explainable overall progress (Section 25)
        # If historical mastery exists for this topic or related concepts, blend it
        prior_masteries = mastery_context.get("concept_mastery", {})
        topic_key = topic.lower().replace(" ", "_")
        prior_topic_score = prior_masteries.get(topic_key)

        if prior_topic_score is not None:
            # 35% prior historical mastery + 65% current formal assessment
            blended = (0.35 * prior_topic_score) + (0.65 * score.percentage)
            overall_progress = round(blended, 4)
        else:
            # Initial baseline: current assessment percentage
            overall_progress = round(score.percentage, 4)

        # 3. Formulate revision recommendations
        recs = self.revision_engine.generate_recommendations(
            weak_areas=weak_areas,
            concept_results=concept_results,
            misconceptions=misconceptions
        )

        # 4. Formulate next-topic recommendation (with strict No-Evidence Rule)
        next_topic, nxt_reason = self.next_topic_engine.recommend_next_topic(
            topic=topic,
            strong_areas=strong_areas,
            weak_areas=weak_areas,
            overall_score=score.percentage,
            learning_path=learning_path
        )

        # 5. Extract lists for clean presentation
        concepts_understood = [
            cr.concept.replace("_", " ").title()
            for cr in concept_results
            if cr.status == "strong"
        ]
        strong_names = [s.replace("_", " ").title() for s in strong_areas]
        weak_names = [w.concept.replace("_", " ").title() for w in weak_areas]
        misc_names = [m.misconception for m in misconceptions]
        revision_concept_names = [
            cr.concept.replace("_", " ").title()
            for cr in concept_results
            if cr.revision_required
        ]

        # 6. Generate human-readable summary
        summary = self._generate_human_summary(
            topic=topic,
            score=score,
            strong_names=strong_names,
            weak_names=weak_names,
            misc_items=misconceptions,
            recommendations=recs,
            next_topic=next_topic
        )

        report = LearningReport(
            student_id=student_id,
            lesson_id=lesson_id,
            assessment_id=assessment_id,
            topic=topic,
            score=score,
            concepts_understood=concepts_understood,
            strong_areas=strong_names,
            weak_areas=weak_names,
            misconceptions=misc_names,
            concepts_requiring_revision=revision_concept_names,
            recommended_revision=recs,
            recommended_next_topic=next_topic,
            next_topic_reasoning=nxt_reason,
            overall_progress=overall_progress,
            human_readable_summary=summary,
            completed_at=datetime.now(timezone.utc).isoformat()
        )

        # 7. Emit durable evidence to Agent 3 (Section 28)
        concept_scores_dict = {cr.concept: cr.score for cr in concept_results}
        self.profile_bridge.emit_assessment_evidence(
            student_id=student_id,
            assessment_id=assessment_id,
            lesson_id=lesson_id,
            topic=topic,
            score=score.percentage,
            concept_scores=concept_scores_dict,
            weak_concepts=weak_names,
            strong_concepts=strong_names,
            misconceptions=misc_names
        )

        return report

    def _generate_human_summary(
        self,
        topic: str,
        score: ScoreSummary,
        strong_names: List[str],
        weak_names: List[str],
        misc_items: List[AggregatedMisconception],
        recommendations: List[RevisionRecommendation],
        next_topic: Optional[str]
    ) -> str:
        """
        Synthesizes concise, grounded, non-hallucinatory pedagogical feedback.
        Adheres to Section 55: Reports specific concepts, not vague course generalizations.
        """
        parts = []

        # Overall performance note
        pct = int(score.percentage * 100)
        parts.append(f"You achieved a score of {score.raw}/{score.max} ({pct}%).")

        # Strong areas
        if strong_names:
            parts.append(f"You demonstrated strong proficiency in {', '.join(strong_names)}.")
        else:
            parts.append("You have established initial foundations across the introductory concepts.")

        # Weak areas & Misconceptions (Section 55: specific concept, not 'weak in topic')
        if weak_names:
            parts.append(f"Your primary area for revision is {', '.join(weak_names)}.")
        
        if misc_items:
            misc_texts = [m.misconception for m in misc_items]
            parts.append(f"Specifically, we observed: {'; '.join(misc_texts)}.")

        # Key recommendation
        if recommendations:
            top_rec = recommendations[0]
            parts.append(f"Recommended action: {top_rec.reason}")

        # Next topic
        if next_topic:
            parts.append(f"Once revision is complete, your suggested next topic is {next_topic}.")

        return " ".join(parts)


report_service = ReportService()
