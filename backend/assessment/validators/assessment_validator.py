"""
Assessment & Question Validator conforming to Section 12 & Section 49.
Enforces strict safety, structure, and pedagogical completeness rules.
"""

from typing import List, Dict, Any, Tuple, Optional
from backend.assessment.models.question import AssessmentQuestion
from backend.assessment.models.config import AssessmentConfig


class AssessmentValidationError(Exception):
    """Raised when an assessment or question fails structural validation."""
    def __init__(self, message: str, errors: Optional[List[str]] = None):
        super().__init__(message)
        self.errors = errors or [message]


class AssessmentValidator:
    """
    Validates assessments and questions before they become active.
    Checks structure, completeness, duplicate IDs, difficulty bounds, and MCQ correctness.
    """

    @classmethod
    def validate_question(cls, question: AssessmentQuestion) -> List[str]:
        """
        Validates a single AssessmentQuestion.
        Returns a list of error strings (empty if valid).
        """
        errors: List[str] = []

        # 1. Question ID & Text
        if not question.question_id or not question.question_id.strip():
            errors.append("Question must have a non-empty question_id.")
        if not question.text or not question.text.strip():
            errors.append(f"Question '{question.question_id}' text is empty.")

        # 2. Expected concept
        if not question.expected_concept or not question.expected_concept.strip():
            errors.append(f"Question '{question.question_id}' has no expected_concept specified.")

        # 3. Difficulty bounds
        if question.difficulty < 0.0 or question.difficulty > 1.0:
            errors.append(
                f"Question '{question.question_id}' difficulty {question.difficulty} must be between 0.0 and 1.0."
            )

        # 4. Points weighting
        if question.points <= 0.0:
            errors.append(f"Question '{question.question_id}' points ({question.points}) must be > 0.")

        # 5. Type-specific checks
        qtype = question.type
        if qtype == "mcq":
            if not question.options or len(question.options) < 2:
                errors.append(f"MCQ question '{question.question_id}' must have at least 2 options.")
            else:
                # Check for empty options
                if any(not opt or not str(opt).strip() for opt in question.options):
                    errors.append(f"MCQ question '{question.question_id}' contains empty options.")
            
            if not question.correct_option or not str(question.correct_option).strip():
                errors.append(f"MCQ question '{question.question_id}' must specify correct_option.")
            elif question.options:
                # Validate correct_option exists either as exact text, or as letter (A, B, C, D), or index
                matched = False
                correct_str = str(question.correct_option).strip()
                # Exact text match
                if any(correct_str.lower() == opt.strip().lower() for opt in question.options):
                    matched = True
                # Letter match: A, B, C, D
                letter_map = {"A": 0, "B": 1, "C": 2, "D": 3, "E": 4}
                if correct_str.upper() in letter_map:
                    idx = letter_map[correct_str.upper()]
                    if idx < len(question.options):
                        matched = True
                # Integer index match
                if correct_str.isdigit():
                    idx = int(correct_str)
                    if 0 <= idx < len(question.options):
                        matched = True

                if not matched:
                    errors.append(
                        f"MCQ question '{question.question_id}' correct_option '{question.correct_option}' "
                        f"does not match any of the provided options: {question.options}."
                    )

        elif qtype == "numerical":
            if question.expected_value is None:
                errors.append(f"Numerical question '{question.question_id}' must specify expected_value.")
            if question.tolerance is not None and question.tolerance < 0.0:
                errors.append(f"Numerical question '{question.question_id}' tolerance must be non-negative.")

        elif qtype in ["short_answer", "conceptual", "problem_solving", "application", "explain_in_own_words"]:
            if not question.expected_answer and not question.expected_concept:
                errors.append(
                    f"Question '{question.question_id}' of type '{qtype}' must provide expected_answer or expected_concept."
                )

        return errors

    @classmethod
    def validate_assessment(
        cls,
        questions: List[AssessmentQuestion],
        config: Optional[AssessmentConfig] = None
    ) -> Tuple[bool, List[str]]:
        """
        Validates the complete set of questions for an assessment.
        Returns (is_valid, errors).
        """
        errors: List[str] = []

        # Check at least one question exists
        if not questions:
            errors.append("Assessment must contain at least one question.")
            return False, errors

        # Check total points > 0
        total_points = sum(q.points for q in questions)
        if total_points <= 0.0:
            errors.append(f"Assessment total points ({total_points}) must be greater than 0.")

        # Check duplicate question IDs
        seen_ids = set()
        for q in questions:
            if q.question_id in seen_ids:
                errors.append(f"Duplicate question ID detected: '{q.question_id}'.")
            seen_ids.add(q.question_id)

            # Validate each question
            q_errors = cls.validate_question(q)
            errors.extend(q_errors)

        # Check coverage if required in config (advisory / token overlap)
        if config and config.coverage:
            import re
            assessed_tokens = set()
            for q in questions:
                for token in re.split(r"[\s_()&,.-]+", q.expected_concept.lower()):
                    if len(token) > 2:
                        assessed_tokens.add(token)
            coverage_tokens = set()
            for c in config.coverage:
                for token in re.split(r"[\s_()&,.-]+", c.lower()):
                    if len(token) > 2:
                        coverage_tokens.add(token)
            common = assessed_tokens.intersection(coverage_tokens)
            # Coverage is advisory; does not reject valid assessments

        is_valid = len(errors) == 0
        return is_valid, errors


    @classmethod
    def ensure_valid(
        cls,
        questions: List[AssessmentQuestion],
        config: Optional[AssessmentConfig] = None
    ) -> None:
        """Helper that raises AssessmentValidationError if invalid."""
        is_valid, errors = cls.validate_assessment(questions, config)
        if not is_valid:
            raise AssessmentValidationError(
                f"Assessment validation failed with {len(errors)} errors: {'; '.join(errors)}",
                errors=errors
            )


assessment_validator = AssessmentValidator()
