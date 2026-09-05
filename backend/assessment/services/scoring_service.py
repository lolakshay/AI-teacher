"""
Assessment Scoring Service conforming to Sections 15, 16, 27, 32, 35, 36.
Provides weighted scoring across MCQ, Numerical, Conceptual, and Short Answer question types.
Delegates open-ended evaluation to Agent 6 via evaluator_bridge.
"""

import re
import math
import logging
from typing import List, Dict, Any, Optional, Tuple

from backend.assessment.models.question import AssessmentQuestion
from backend.assessment.models.session import AssessmentResponse
from backend.assessment.models.result import (
    QuestionResult, ScoreSummary, ResultClassification
)
from backend.assessment.providers.evaluator_bridge import evaluator_bridge, EvaluatorBridge

logger = logging.getLogger(__name__)


class ScoringService:
    """
    Evaluates student responses against questions and calculates weighted scores.
    """

    def __init__(self, bridge: Optional[EvaluatorBridge] = None):
        self.bridge = bridge or evaluator_bridge

    def score_response(
        self,
        question: AssessmentQuestion,
        response: Optional[AssessmentResponse],
        language: str = "English"
    ) -> QuestionResult:
        """
        Scores an individual question response.
        Handles MCQ, Numerical, and open-ended evaluation via Agent 6.
        """
        points_possible = question.points

        # 1. Handle missing / skipped response
        if response is None or response.is_skipped or not response.answer or not response.answer.strip():
            return QuestionResult(
                question_id=question.question_id,
                concept=question.expected_concept,
                correctness=0.0,
                points_earned=0.0,
                points_possible=points_possible,
                classification="skipped",
                misconception=None,  # Section 36: Never interpret skipped as misconception
                knowledge_gap="Question was skipped or unattempted.",
                evaluation_confidence=1.0,
                reasoning_quality="No response provided",
                feedback="Question was skipped.",
                is_skipped=True
            )

        answer_text = response.answer.strip()
        qtype = question.type

        # 2. MCQ Scoring
        if qtype == "mcq":
            return self._score_mcq(question, answer_text)

        # 3. Numerical Scoring
        elif qtype == "numerical":
            return self._score_numerical(question, answer_text)

        # 4. Open-ended / Conceptual / Short Answer via Agent 6
        else:
            return self._score_open_ended(question, response, language)

    def _score_mcq(self, question: AssessmentQuestion, answer_text: str) -> QuestionResult:
        options = question.options or []
        correct_target = str(question.correct_option or "").strip()
        ans_clean = answer_text.strip()

        is_correct = False
        letter_map = {"A": 0, "B": 1, "C": 2, "D": 3, "E": 4}

        # Match exact option text
        if ans_clean.lower() == correct_target.lower():
            is_correct = True
        # Match option letter (e.g., student wrote "B" or "b", and correct_option is "B" or option index 1)
        elif ans_clean.upper() in letter_map:
            chosen_idx = letter_map[ans_clean.upper()]
            # Target might be letter
            if correct_target.upper() == ans_clean.upper():
                is_correct = True
            elif chosen_idx < len(options) and options[chosen_idx].strip().lower() == correct_target.lower():
                is_correct = True
        # Check if student wrote "Option B: Ampere" or "B) Ampere"
        elif any(f"({k})" in ans_clean.upper() or f"{k})" in ans_clean.upper() or f"OPTION {k}" in ans_clean.upper() for k in letter_map):
            for k, idx in letter_map.items():
                if (k in ans_clean.upper()) and idx < len(options):
                    if options[idx].strip().lower() == correct_target.lower():
                        is_correct = True
                        break

        correctness = 1.0 if is_correct else 0.0
        points_earned = correctness * question.points
        classification: ResultClassification = "correct" if is_correct else "incorrect"

        return QuestionResult(
            question_id=question.question_id,
            concept=question.expected_concept,
            correctness=correctness,
            points_earned=points_earned,
            points_possible=question.points,
            classification=classification,
            misconception=None if is_correct else "Incorrect multiple-choice option selected.",
            evaluation_confidence=1.0,
            reasoning_quality="Direct choice selection",
            feedback="Correct selection." if is_correct else f"Incorrect. Correct answer: {correct_target}",
            is_skipped=False
        )

    def _score_numerical(self, question: AssessmentQuestion, answer_text: str) -> QuestionResult:
        expected_val = question.expected_value
        if expected_val is None:
            return QuestionResult(
                question_id=question.question_id,
                concept=question.expected_concept,
                correctness=0.0,
                points_earned=0.0,
                points_possible=question.points,
                classification="incorrect",
                feedback="Invalid numerical question configuration (missing expected value)."
            )

        tolerance = question.tolerance if question.tolerance is not None else 0.05

        # Extract numeric value using regex
        # Supports numbers like 2, 2.0, -10.5, 1e-3
        match = re.search(r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?", answer_text)
        if not match:
            return QuestionResult(
                question_id=question.question_id,
                concept=question.expected_concept,
                correctness=0.0,
                points_earned=0.0,
                points_possible=question.points,
                classification="incorrect",
                knowledge_gap="Could not parse a numeric value from the response.",
                evaluation_confidence=1.0,
                feedback=f"Could not parse numeric answer. Expected approximately {expected_val} {question.unit or ''}."
            )

        student_num = float(match.group(0))

        # Check tolerance (relative or absolute)
        abs_diff = abs(student_num - expected_val)
        rel_diff = abs_diff / abs(expected_val) if expected_val != 0 else abs_diff

        # Unit check if specified
        unit_matched = True
        unit_note = ""
        if question.unit:
            unit_pattern = re.compile(rf"\b{re.escape(question.unit)}\b", re.IGNORECASE)
            # Check for common unit synonyms (e.g. A vs Amperes vs amp)
            synonyms = {
                "a": ["a", "amp", "amps", "ampere", "amperes"],
                "v": ["v", "volt", "volts"],
                "ohm": ["ohm", "ohms", "ω"],
                "w": ["w", "watt", "watts"]
            }
            target_unit_key = question.unit.lower().rstrip("s")
            allowed = synonyms.get(target_unit_key, [question.unit.lower()])
            unit_matched = any(re.search(rf"\b{re.escape(u)}\b", answer_text, re.IGNORECASE) for u in allowed)
            if not unit_matched:
                unit_note = f" (Unit '{question.unit}' was missing or unstated)"

        # Check for inverse relationship error (e.g. student did I = V * R instead of I = V / R, or vice-versa)
        misconception = None
        if expected_val != 0 and math.isclose(student_num, 1.0 / expected_val, rel_tol=0.1):
            misconception = "Inverted formula calculation (inverted numerator and denominator)."

        is_exact = abs_diff < 1e-7
        is_within_tol = (rel_diff <= tolerance) or (abs_diff <= tolerance)

        if is_exact or is_within_tol:
            correctness = 1.0
            classification: ResultClassification = "correct"
            feedback = f"Calculated value {student_num} is correct{unit_note}."
            points_earned = question.points
        elif rel_diff <= (tolerance * 3):
            # Minor rounding error (Section 54)
            correctness = 0.85
            classification = "partially_correct"
            feedback = f"Calculated value {student_num} has a small rounding difference from {expected_val}{unit_note}."
            points_earned = 0.85 * question.points
        else:
            correctness = 0.0
            classification = "incorrect"
            feedback = f"Calculated value {student_num} differs significantly from expected {expected_val} {question.unit or ''}."
            points_earned = 0.0

        return QuestionResult(
            question_id=question.question_id,
            concept=question.expected_concept,
            correctness=correctness,
            points_earned=points_earned,
            points_possible=question.points,
            classification=classification,
            misconception=misconception,
            evaluation_confidence=0.98,
            reasoning_quality="Numerical computation",
            feedback=feedback,
            is_skipped=False
        )

    def _score_open_ended(
        self,
        question: AssessmentQuestion,
        response: AssessmentResponse,
        language: str
    ) -> QuestionResult:
        """
        Delegates conceptual and short-answer evaluation to Agent 6.
        """
        agent6_eval = self.bridge.evaluate_response(question, response, language)
        correctness = float(agent6_eval.get("correctness", 0.0))
        classification_str = agent6_eval.get("classification", "incorrect")

        # Map to standard classification
        if classification_str not in [
            "correct", "partially_correct", "incorrect", "misconception", "unclear", "skipped"
        ]:
            classification_str = "correct" if correctness >= 0.8 else ("partially_correct" if correctness >= 0.4 else "incorrect")

        points_earned = correctness * question.points

        return QuestionResult(
            question_id=question.question_id,
            concept=question.expected_concept,
            correctness=correctness,
            points_earned=points_earned,
            points_possible=question.points,
            classification=classification_str,
            misconception=agent6_eval.get("misconception"),
            knowledge_gap=agent6_eval.get("knowledge_gap"),
            evaluation_confidence=agent6_eval.get("confidence", 1.0),
            reasoning_quality=agent6_eval.get("reasoning_quality", "Satisfactory"),
            feedback=agent6_eval.get("teacher_thought", ""),
            is_skipped=False
        )

    def calculate_score_summary(
        self,
        question_results: List[QuestionResult],
        passing_score: float = 0.70
    ) -> ScoreSummary:
        """
        Calculates raw points, max points, percentage, and pass/fail.
        """
        raw = sum(qr.points_earned for qr in question_results)
        max_score = sum(qr.points_possible for qr in question_results)
        percentage = (raw / max_score) if max_score > 0 else 0.0
        # Round percentage to 4 decimal places
        percentage = round(percentage, 4)

        return ScoreSummary(
            raw=round(raw, 2),
            max=round(max_score, 2),
            percentage=percentage,
            passed=percentage >= passing_score
        )


scoring_service = ScoringService()
