"""
Learning Analytics Service conforming to Sections 17, 18, 19, 20, 37, 38, 39, 57.
Processes raw question results into concept-level mastery evidence,
identifies strong and weak areas, aggregates recurring misconceptions,
and analyzes difficulty and question-type breakdowns.
"""

from typing import List, Dict, Any, Optional
from collections import defaultdict

from backend.assessment.models.question import AssessmentQuestion
from backend.assessment.models.result import (
    QuestionResult, ConceptResult, AggregatedMisconception,
    WeakAreaItem, ConceptStatus
)


class AnalyticsService:
    """
    Computes diagnostic learning analytics from multi-question assessment results.
    Strictly evidence-grounded: does not fabricate misconceptions or mastery without evidence.
    """

    def analyze_concepts(
        self,
        questions: List[AssessmentQuestion],
        question_results: List[QuestionResult]
    ) -> List[ConceptResult]:
        """
        Calculates concept-level scores and mastery statuses across all tested concepts.
        """
        # Group results by concept
        concept_points_earned: Dict[str, float] = defaultdict(float)
        concept_points_possible: Dict[str, float] = defaultdict(float)
        concept_attempted: Dict[str, int] = defaultdict(int)
        concept_correct: Dict[str, int] = defaultdict(int)
        concept_misconceptions: Dict[str, List[str]] = defaultdict(list)

        for qr in question_results:
            c = qr.concept
            concept_points_earned[c] += qr.points_earned
            concept_points_possible[c] += qr.points_possible
            if not qr.is_skipped:
                concept_attempted[c] += 1
            if qr.correctness >= 0.75:
                concept_correct[c] += 1
            if qr.misconception and qr.misconception.strip():
                if qr.misconception not in concept_misconceptions[c]:
                    concept_misconceptions[c].append(qr.misconception)

        concept_results: List[ConceptResult] = []
        # Ensure all concepts present in questions are represented
        all_concepts = list(dict.fromkeys([q.expected_concept for q in questions]))

        for c in all_concepts:
            possible = concept_points_possible.get(c, 0.0)
            earned = concept_points_earned.get(c, 0.0)
            score = (earned / possible) if possible > 0 else 0.0
            score = round(score, 4)
            attempted = concept_attempted.get(c, 0)
            correct = concept_correct.get(c, 0)
            misc_list = concept_misconceptions.get(c, [])

            # Status classification
            status: ConceptStatus = "unknown"
            if attempted == 0:
                status = "unknown"
            elif score >= 0.80 and len(misc_list) == 0:
                status = "strong"
            elif score >= 0.50:
                status = "developing"
            else:
                status = "weak"

            # If a misconception was explicitly detected, concept cannot be considered strong
            if misc_list and status == "strong":
                status = "developing"

            revision_required = (status in ["weak", "developing"]) or (len(misc_list) > 0)

            concept_results.append(
                ConceptResult(
                    concept=c,
                    score=score,
                    questions_attempted=attempted,
                    questions_correct=correct,
                    status=status,
                    revision_required=revision_required,
                    misconceptions=misc_list
                )
            )

        return concept_results

    def detect_weak_areas(
        self,
        concept_results: List[ConceptResult]
    ) -> List[WeakAreaItem]:
        """
        Identifies specific weak concepts with diagnostic pedagogical rationale.
        Does not merely list incorrect question IDs; groups by conceptual difficulty.
        """
        weak_areas: List[WeakAreaItem] = []

        for cr in concept_results:
            if cr.status == "weak" or cr.score < 0.60 or cr.misconceptions:
                reasons = []
                if cr.misconceptions:
                    reasons.append(f"Misconception detected: '{'; '.join(cr.misconceptions)}'")
                if cr.score < 0.40:
                    reasons.append(f"Low accuracy ({int(cr.score * 100)}%) across attempted problems")
                elif cr.score < 0.60:
                    reasons.append(f"Developing understanding ({int(cr.score * 100)}%) with inconsistent application")
                elif cr.questions_attempted == 0:
                    reasons.append("Unattempted during assessment")

                weak_areas.append(
                    WeakAreaItem(
                        concept=cr.concept,
                        score=cr.score,
                        reason="; ".join(reasons) if reasons else "Requires revision",
                        misconceptions=cr.misconceptions
                    )
                )

        return weak_areas

    def detect_strong_areas(
        self,
        concept_results: List[ConceptResult]
    ) -> List[str]:
        """
        Identifies concepts with solid evidence of mastery to avoid unnecessary reteaching.
        """
        strong_areas: List[str] = []
        for cr in concept_results:
            if cr.status == "strong" and cr.score >= 0.80 and not cr.misconceptions:
                strong_areas.append(cr.concept)
        return strong_areas

    def aggregate_misconceptions(
        self,
        question_results: List[QuestionResult]
    ) -> List[AggregatedMisconception]:
        """
        Aggregates individual misconceptions across questions.
        Counts frequency and confidence.
        Section 20 & 57: Never fabricates misconceptions without evidence.
        """
        misc_data: Dict[str, Dict[str, Any]] = {}

        for qr in question_results:
            if qr.misconception and qr.misconception.strip():
                m_key = qr.misconception.strip().lower()
                if m_key not in misc_data:
                    misc_data[m_key] = {
                        "misconception": qr.misconception.strip(),
                        "concept": qr.concept,
                        "frequency": 0,
                        "confidences": [],
                        "descriptions": []
                    }
                misc_data[m_key]["frequency"] += 1
                misc_data[m_key]["confidences"].append(qr.evaluation_confidence)
                if qr.feedback:
                    misc_data[m_key]["descriptions"].append(qr.feedback)

        aggregated: List[AggregatedMisconception] = []
        for m_key, info in misc_data.items():
            avg_conf = sum(info["confidences"]) / len(info["confidences"]) if info["confidences"] else 1.0
            desc = (
                f"Repeated in {info['frequency']} response(s)"
                if info["frequency"] > 1
                else "Identified in student response"
            )
            aggregated.append(
                AggregatedMisconception(
                    misconception=info["misconception"],
                    concept=info["concept"],
                    frequency=info["frequency"],
                    confidence=round(avg_conf, 2),
                    description=desc
                )
            )

        # Sort by highest frequency first
        aggregated.sort(key=lambda m: m.frequency, reverse=True)
        return aggregated

    def compute_difficulty_breakdown(
        self,
        questions: List[AssessmentQuestion],
        question_results: List[QuestionResult]
    ) -> Dict[str, Dict[str, float]]:
        """
        Section 39: Calculates accuracy broken down by easy, medium, and hard tiers.
        """
        q_map = {q.question_id: q for q in questions}
        tier_data: Dict[str, Dict[str, float]] = {
            "easy": {"earned": 0.0, "possible": 0.0, "count": 0},
            "medium": {"earned": 0.0, "possible": 0.0, "count": 0},
            "hard": {"earned": 0.0, "possible": 0.0, "count": 0}
        }

        for qr in question_results:
            q = q_map.get(qr.question_id)
            diff = q.difficulty if q else 0.4
            if diff < 0.35:
                tier = "easy"
            elif diff < 0.65:
                tier = "medium"
            else:
                tier = "hard"

            tier_data[tier]["earned"] += qr.points_earned
            tier_data[tier]["possible"] += qr.points_possible
            tier_data[tier]["count"] += 1

        breakdown: Dict[str, Dict[str, float]] = {}
        for tier, data in tier_data.items():
            if data["possible"] > 0:
                acc = round(data["earned"] / data["possible"], 4)
            else:
                acc = 0.0
            breakdown[tier] = {
                "accuracy": acc,
                "points_earned": round(data["earned"], 2),
                "points_possible": round(data["possible"], 2),
                "question_count": data["count"]
            }

        return breakdown

    def compute_question_type_breakdown(
        self,
        questions: List[AssessmentQuestion],
        question_results: List[QuestionResult]
    ) -> Dict[str, Dict[str, float]]:
        """
        Section 38: Calculates accuracy broken down by question type (mcq, numerical, conceptual, etc.).
        """
        q_map = {q.question_id: q for q in questions}
        type_data: Dict[str, Dict[str, float]] = defaultdict(lambda: {"earned": 0.0, "possible": 0.0, "count": 0})

        for qr in question_results:
            q = q_map.get(qr.question_id)
            qtype = q.type if q else "conceptual"
            type_data[qtype]["earned"] += qr.points_earned
            type_data[qtype]["possible"] += qr.points_possible
            type_data[qtype]["count"] += 1

        breakdown: Dict[str, Dict[str, float]] = {}
        for qtype, data in type_data.items():
            if data["possible"] > 0:
                acc = round(data["earned"] / data["possible"], 4)
            else:
                acc = 0.0
            breakdown[qtype] = {
                "accuracy": acc,
                "points_earned": round(data["earned"], 2),
                "points_possible": round(data["possible"], 2),
                "question_count": data["count"]
            }

        return breakdown


analytics_service = AnalyticsService()
