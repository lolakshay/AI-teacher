"""
Revision Recommendation Engine conforming to Section 21 & Section 48.
Generates prioritized, targeted, and pedagogically grounded revision activities.
"""

from typing import List, Dict, Any, Optional
from backend.assessment.models.report import RevisionRecommendation, RevisionPriority
from backend.assessment.models.result import WeakAreaItem, AggregatedMisconception, ConceptResult


class RevisionEngine:
    """
    Synthesizes targeted revision plans from weak areas, concept scores, and misconceptions.
    Avoids generic 'study more' advice in favor of specific worked examples and concept reviews.
    """

    def generate_recommendations(
        self,
        weak_areas: List[WeakAreaItem],
        concept_results: List[ConceptResult],
        misconceptions: List[AggregatedMisconception]
    ) -> List[RevisionRecommendation]:
        recommendations: List[RevisionRecommendation] = []
        seen_concepts = set()

        # Map concept to misconceptions
        concept_to_misc: Dict[str, List[AggregatedMisconception]] = {}
        for m in misconceptions:
            concept_to_misc.setdefault(m.concept, []).append(m)

        for wa in weak_areas:
            c = wa.concept
            if c in seen_concepts:
                continue
            seen_concepts.add(c)

            cr = next((r for r in concept_results if r.concept == c), None)
            score = cr.score if cr else wa.score
            misc_items = concept_to_misc.get(c, [])

            # Determine Priority (Section 48)
            # High: repeated misconception, or severe failure (score < 0.4)
            # Medium: score 0.40 - 0.69
            # Low: minor error (score >= 0.70)
            has_repeated_misc = any(m.frequency > 1 for m in misc_items)
            has_any_misc = len(misc_items) > 0 or len(wa.misconceptions) > 0

            priority: RevisionPriority = "medium"
            if has_repeated_misc or score < 0.40:
                priority = "high"
            elif has_any_misc:
                priority = "high" if score < 0.60 else "medium"
            elif score >= 0.70:
                priority = "low"

            # Formulate targeted pedagogical activity
            c_lower = c.lower().replace("_", " ")
            activity = "concept_review"
            time_mins = 10

            if "inverse" in c_lower or "proportional" in c_lower:
                activity = "worked_examples_and_physical_analogy"
                reason = (
                    "Review the inverse relationship between resistance and current using I = V/R, "
                    "then solve 2 constant-voltage examples."
                )
                time_mins = 10
            elif "formula" in c_lower or "equation" in c_lower or "calculation" in c_lower:
                activity = "guided_calculation_practice"
                reason = f"Practice algebraic manipulation of {c_lower} and verify units."
                time_mins = 8
            elif has_any_misc:
                misc_names = [m.misconception for m in misc_items] or wa.misconceptions
                reason = f"Resolve misconception '{'; '.join(misc_names)}' via guided contrasting cases."
                activity = "contrasting_examples"
                time_mins = 12
            else:
                reason = f"Reinforce core principles of {c_lower} through guided practice problems."
                activity = "practice_problems"
                time_mins = 10

            recommendations.append(
                RevisionRecommendation(
                    concept=c,
                    priority=priority,
                    reason=reason,
                    recommended_activity=activity,
                    estimated_time_minutes=time_mins
                )
            )

        # Sort recommendations: high priority first, then medium, then low
        priority_order = {"high": 0, "medium": 1, "low": 2}
        recommendations.sort(key=lambda r: priority_order.get(r.priority, 1))
        return recommendations


revision_engine = RevisionEngine()
