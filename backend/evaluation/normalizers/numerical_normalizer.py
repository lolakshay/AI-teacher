"""
Numerical Normalization and Tolerance Verification for Student Responses.
Conforms to Section 31.
"""

import re
import math
from typing import Optional, Tuple
from pydantic import BaseModel


class NumericalParsed(BaseModel):
    value: Optional[float] = None
    unit: Optional[str] = None
    raw_text: str = ""


class NumericalComparisonResult(BaseModel):
    is_valid_number: bool = False
    parsed_value: Optional[float] = None
    parsed_unit: Optional[str] = None
    expected_value: Optional[float] = None
    expected_unit: Optional[str] = None
    value_correct: bool = False
    unit_correct: bool = False
    relative_error: Optional[float] = None
    absolute_error: Optional[float] = None


class NumericalNormalizer:
    """
    Parses and verifies numerical values and associated scientific units.
    """

    UNIT_CANONICAL_MAP = {
        "a": "a", "amp": "a", "amps": "a", "ampere": "a", "amperes": "a",
        "v": "v", "volt": "v", "volts": "v",
        "ohm": "ohm", "ohms": "ohm", "ω": "ohm",
        "w": "w", "watt": "w", "watts": "w",
        "j": "j", "joule": "j", "joules": "j",
        "hz": "hz", "hertz": "hz",
        "s": "s", "sec": "s", "second": "s", "seconds": "s",
        "m": "m", "meter": "m", "meters": "m",
        "m/s": "m/s", "m/sec": "m/s", "mps": "m/s",
        "m/s^2": "m/s^2", "m/s2": "m/s^2",
        "n": "n", "newton": "n", "newtons": "n",
        "c": "c", "coulomb": "c", "coulombs": "c",
        "kg": "kg", "kilogram": "kg", "kilograms": "kg",
    }

    # Matches fractions (e.g. 1/2) first, then floats/scientific notation
    NUMBER_PATTERN = re.compile(
        r"([+-]?\d+(?:\.\d+)?\s*/\s*\d+(?:\.\d+)?|[+-]?(?:\d+(?:\.\d+)?|\.\d+)(?:[eE][+-]?\d+)?)"
    )

    @classmethod
    def canonicalize_unit(cls, unit_str: Optional[str]) -> Optional[str]:
        if not unit_str:
            return None
        cleaned = unit_str.strip().lower().rstrip(".,")
        return cls.UNIT_CANONICAL_MAP.get(cleaned, cleaned)

    @classmethod
    def parse_numerical_string(cls, text: str) -> NumericalParsed:
        """
        Extracts the first number and following potential unit.
        """
        if not text:
            return NumericalParsed(raw_text=text)

        cleaned = text.strip()
        match = cls.NUMBER_PATTERN.search(cleaned)
        if not match:
            return NumericalParsed(raw_text=cleaned)

        num_str = match.group(1).replace(" ", "")
        try:
            if "/" in num_str:
                parts = num_str.split("/")
                val = float(parts[0]) / float(parts[1])
            else:
                val = float(num_str)
        except (ValueError, ZeroDivisionError):
            return NumericalParsed(raw_text=cleaned)

        # Look for text after or before the number for units
        after = cleaned[match.end():].strip()
        unit_token = None
        if after:
            # First word in 'after'
            first_word = after.split()[0]
            unit_token = cls.canonicalize_unit(first_word)

        return NumericalParsed(value=val, unit=unit_token, raw_text=cleaned)

    @classmethod
    def compare(
        cls,
        student_text: str,
        expected_text_or_num: str,
        expected_unit: Optional[str] = None,
        tolerance: float = 0.05,
        tolerance_type: str = "relative",
        require_unit: bool = False
    ) -> NumericalComparisonResult:
        """
        Compares student response against expected numerical answer with tolerance and unit validation.
        """
        student_parsed = cls.parse_numerical_string(student_text)
        expected_parsed = cls.parse_numerical_string(str(expected_text_or_num))

        if student_parsed.value is None or expected_parsed.value is None:
            return NumericalComparisonResult(
                is_valid_number=False,
                parsed_value=student_parsed.value,
                parsed_unit=student_parsed.unit,
                expected_value=expected_parsed.value,
                expected_unit=cls.canonicalize_unit(expected_unit or expected_parsed.unit),
                value_correct=False,
                unit_correct=False
            )

        target_unit = cls.canonicalize_unit(expected_unit or expected_parsed.unit)
        s_val = student_parsed.value
        e_val = expected_parsed.value

        abs_err = abs(s_val - e_val)
        rel_err = abs_err / max(abs(e_val), 1e-9)

        if tolerance_type == "absolute":
            val_correct = abs_err <= tolerance
        else:
            val_correct = rel_err <= tolerance

        # Unit evaluation
        if target_unit is None:
            unit_correct = True
        else:
            if student_parsed.unit:
                unit_correct = student_parsed.unit == target_unit
            else:
                # Student gave no unit
                unit_correct = not require_unit

        return NumericalComparisonResult(
            is_valid_number=True,
            parsed_value=s_val,
            parsed_unit=student_parsed.unit,
            expected_value=e_val,
            expected_unit=target_unit,
            value_correct=val_correct,
            unit_correct=unit_correct,
            relative_error=rel_err,
            absolute_error=abs_err
        )


numerical_normalizer = NumericalNormalizer()
