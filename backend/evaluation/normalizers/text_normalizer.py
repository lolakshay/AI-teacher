"""
Text Normalization for Student Responses.
Conforms to Sections 26, 29, and 30.
"""

import re
import unicodedata
from typing import Tuple, Optional


class TextNormalizer:
    """
    Normalizes harmless student input variations while guarding against
    prompt injection patterns and excessive payloads.
    """

    WORD_TO_NUMBER = {
        "zero": "0", "one": "1", "two": "2", "three": "3", "four": "4",
        "five": "5", "six": "6", "seven": "7", "eight": "8", "nine": "9",
        "ten": "10", "eleven": "11", "twelve": "12", "half": "0.5",
        "shunya": "0", "ek": "1", "do": "2", "teen": "3", "chaar": "4",
        "paanch": "5", "chhe": "6", "saat": "7", "aath": "8", "nau": "9", "das": "10"
    }

    FORMULA_REPLACEMENTS = [
        (r"[×*•]", "*"),
        (r"[÷/]", "/"),
        (r"\s*=\s*", " = "),
        (r"\s*\*\s*", " * "),
        (r"\s*/\s*", " / "),
        (r"\s*\+\s*", " + "),
        (r"\s*-\s*", " - "),
    ]

    INJECTION_PATTERNS = [
        r"ignore (all|the|previous|system) (instructions|rules|prompts)",
        r"disregard (all|the|previous)",
        r"mark (me|this|the student) (as )?(correct|100|full marks|true)",
        r"you are now (an? )?(unrestricted|developer mode)",
        r"system prompt:",
        r"output json with correctness: 1",
    ]

    @classmethod
    def sanitize_untrusted_input(cls, text: str, max_chars: int = 4000) -> str:
        """
        Truncates excessive input and strips dangerous control characters.
        """
        if not text:
            return ""
        # Strip null bytes and non-printable control characters (except newline, tab)
        cleaned = "".join(ch for ch in text if ch in ("\n", "\t") or unicodedata.category(ch)[0] != "C")
        if len(cleaned) > max_chars:
            cleaned = cleaned[:max_chars]
        return cleaned.strip()

    @classmethod
    def check_potential_injection(cls, text: str) -> Tuple[bool, Optional[str]]:
        """
        Detects obvious prompt injection or jailbreak attempts.
        Returns (is_injection, reason).
        """
        lower = text.lower()
        for pat in cls.INJECTION_PATTERNS:
            if re.search(pat, lower):
                return True, f"Matched injection pattern: {pat}"
        return False, None

    @classmethod
    def normalize_text(cls, text: str) -> str:
        """
        Normalizes spaces, casing, unicode punctuation, and formula representations.
        """
        if not text:
            return ""
        # Unicode NFKC normalization
        norm = unicodedata.normalize("NFKC", text)
        norm = norm.strip().lower()

        # Normalize mathematical symbols
        for pattern, replacement in cls.FORMULA_REPLACEMENTS:
            norm = re.sub(pattern, replacement, norm)

        # Normalize multiple spaces and newlines
        norm = re.sub(r"\s+", " ", norm)
        return norm

    @classmethod
    def extract_word_number(cls, text: str) -> str:
        """
        Replaces spelled out numbers like 'four' with '4'.
        """
        words = text.split()
        converted = [cls.WORD_TO_NUMBER.get(w.lower(), w) for w in words]
        return " ".join(converted)


text_normalizer = TextNormalizer()
