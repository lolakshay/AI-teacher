"""
Speech Normalizer for STEM and Mathematical Pronunciation (Agent 5)
Converts LaTeX, mathematical equations, scientific notation, and units
into natural spoken phonetics while strictly preserving display_text for visuals.
"""

import re
from typing import Tuple

class SpeechNormalizer:
    """
    Normalizes educational and mathematical text for human-like TTS delivery.
    """

    # Common STEM Greek letters
    GREEK_MAP = {
        r"\\alpha": "alpha",
        r"\\beta": "beta",
        r"\\gamma": "gamma",
        r"\\delta": "delta",
        r"\\Delta": "delta",
        r"\\theta": "theta",
        r"\\lambda": "lambda",
        r"\\mu": "micro",
        r"\\pi": "pi",
        r"\\sigma": "sigma",
        r"\\omega": "omega",
        r"\\Omega": "ohms",
        r"Ω": "ohms",
        r"Δ": "delta",
        r"π": "pi",
        r"θ": "theta",
    }

    # Units with preceding numbers e.g. 5V, 10A, 20Ω, 50Hz
    UNIT_PATTERNS = [
        (r"(\d+(?:\.\d+)?)\s*(?:V|volts?)\b", r"\1 volts"),
        (r"(\d+(?:\.\d+)?)\s*(?:A|amps?|amperes?)\b", r"\1 amperes"),
        (r"(\d+(?:\.\d+)?)\s*(?:Ω|ohms?|\\Omega)\b", r"\1 ohms"),
        (r"(\d+(?:\.\d+)?)\s*(?:Hz|hertz)\b", r"\1 hertz"),
        (r"(\d+(?:\.\d+)?)\s*(?:W|watts?)\b", r"\1 watts"),
        (r"(\d+(?:\.\d+)?)\s*m/s\^2\b", r"\1 meters per second squared"),
        (r"(\d+(?:\.\d+)?)\s*m/s²\b", r"\1 meters per second squared"),
        (r"(\d+(?:\.\d+)?)\s*m/s\b", r"\1 meters per second"),
    ]

    def normalize(self, raw_text: str, language: str = "en") -> Tuple[str, str]:
        """
        Takes raw teaching text and returns a tuple:
        (display_text, spoken_text)
        Preserves display_text exactly as given for Agent 4's visual rendering.
        """
        display_text = raw_text.strip()
        spoken = display_text

        # 1. Replace fractions \frac{a}{b} -> "a over b"
        spoken = re.sub(r"\\frac\{([^{}]+)\}\{([^{}]+)\}", r"\1 over \2", spoken)

        # 2. Mathematical exponents
        spoken = re.sub(r"([a-zA-Z0-9]+)\^2\b", r"\1 squared", spoken)
        spoken = re.sub(r"([a-zA-Z0-9]+)²", r"\1 squared", spoken)
        spoken = re.sub(r"([a-zA-Z0-9]+)\^3\b", r"\1 cubed", spoken)
        spoken = re.sub(r"([a-zA-Z0-9]+)³", r"\1 cubed", spoken)
        spoken = re.sub(r"([a-zA-Z0-9]+)\^([a-zA-Z0-9]+)", r"\1 to the power of \2", spoken)

        # 3. Subscripts
        spoken = re.sub(r"([a-zA-Z]+)_([0-9]+)", r"\1 \2", spoken)

        # 4. Canonical formulas & relations
        # V = I * R or V = I × R or V = I \times R
        spoken = re.sub(r"\bV\s*=\s*I\s*(?:×|\*|\\times)\s*R\b", "V equals I multiplied by R", spoken, flags=re.IGNORECASE)
        spoken = re.sub(r"\bI\s*=\s*V\s*(?:/|÷|\\div)\s*R\b", "I equals V divided by R", spoken, flags=re.IGNORECASE)
        spoken = re.sub(r"\bR\s*=\s*V\s*(?:/|÷|\\div)\s*I\b", "R equals V divided by I", spoken, flags=re.IGNORECASE)
        spoken = re.sub(r"\bF\s*=\s*m\s*a\b", "F equals m a", spoken)
        spoken = re.sub(r"\bF\s*=\s*ma\b", "F equals m a", spoken)
        spoken = re.sub(r"\bE\s*=\s*m\s*c\s*squared\b", "E equals m c squared", spoken)
        spoken = re.sub(r"\bE\s*=\s*mc\^2\b", "E equals m c squared", spoken)
        spoken = re.sub(r"\by\s*=\s*m\s*x\s*\+\s*c\b", "y equals m x plus c", spoken)
        spoken = re.sub(r"\ba\s*squared\s*\+\s*b\s*squared\s*=\s*c\s*squared\b", "a squared plus b squared equals c squared", spoken)

        # 5. Integrals & Calculus
        spoken = re.sub(r"(?:\\int|∫)\s*([a-zA-Z0-9\(\)]+)\s*d([a-zA-Z])", r"integral of \1 d \2", spoken)

        # 6. Replace Greek Symbols
        for symbol, word in self.GREEK_MAP.items():
            spoken = re.sub(symbol, f" {word} ", spoken)

        # 7. Units
        for pattern, repl in self.UNIT_PATTERNS:
            spoken = re.sub(pattern, repl, spoken)

        # 8. General mathematical operators
        spoken = spoken.replace(" × ", " multiplied by ")
        spoken = spoken.replace(" ÷ ", " divided by ")
        spoken = spoken.replace(" <= ", " is less than or equal to ")
        spoken = spoken.replace(" >= ", " is greater than or equal to ")
        spoken = spoken.replace(" != ", " is not equal to ")
        spoken = spoken.replace(" ≈ ", " is approximately equal to ")

        # 9. Clean up LaTeX artifacts (\text{...}, \mathbf{...}, $, etc.)
        spoken = re.sub(r"\\[a-zA-Z]+\{([^{}]+)\}", r"\1", spoken)
        spoken = spoken.replace("$", "")
        spoken = spoken.replace("\\", "")

        # 10. Clean up extra whitespace and punctuation spacing
        spoken = re.sub(r"\s+", " ", spoken).strip()

        return display_text, spoken

speech_normalizer = SpeechNormalizer()
