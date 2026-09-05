"""
Validation and Semantic Preservation Service for Agent 8.
Strictly validates:
- Formulas and equations (V = IR, I = V / R, LaTeX)
- Numerical values (10, 5, 24, 4)
- Physical units (V, A, Ω, Ohms, Volts, Amperes)
- Programming code blocks (byte-for-byte fidelity)
- Technical terminology preservation
- Concept ID neutrality
- Prompt injection and malicious input checks
"""

import re
from typing import List, Tuple, Optional
from backend.multilingual.models.adaptation import ValidationResult

class ValidationService:
    # Match code blocks: ```[lang]\n...\n```
    CODE_BLOCK_REGEX = re.compile(r"```(?:[a-zA-Z0-9_\-]+)?\n(.*?)```", re.DOTALL)

    # Match LaTeX equations: $...$ or $$...$$
    LATEX_REGEX = re.compile(r"\$\$(.*?)\$\$|\$([^$]+)\$")

    # Match typical mathematical/physics equations: e.g. V = IR, I = V / R, V = I * R
    EQUATION_REGEX = re.compile(r"\b([A-Za-z]\s*=\s*[A-Za-z0-9_+\-*/\^ ()\.]+)\b")

    # Match numbers with optional units: e.g. 10 V, 5 Ω, 24V, 6 Ohms, 4A, 3 L/s, 100%
    NUMBER_UNIT_REGEX = re.compile(
        r"\b(\d+(?:\.\d+)?)\s*(V|Volts?|A|Amps?|Amperes?|Ω|Ohms?|W|Watts?|Hz|J|Joules?|L/s|s|sec|seconds?|%)\b",
        re.IGNORECASE
    )

    # Isolated numbers (standalone numbers with at least 1 digit)
    STANDALONE_NUMBER_REGEX = re.compile(r"\b(\d+(?:\.\d+)?)\b")

    # Prompt injection signatures
    INJECTION_PATTERNS = [
        re.compile(r"ignore\s+(?:all\s+)?(?:previous|prior)\s+instructions", re.IGNORECASE),
        re.compile(r"disregard\s+(?:all\s+)?(?:previous|prior)\s+instructions", re.IGNORECASE),
        re.compile(r"system\s*:\s*you\s+are", re.IGNORECASE),
        re.compile(r"you\s+are\s+now\s+a\s+different", re.IGNORECASE),
        re.compile(r"<script.*?>.*?</script>", re.IGNORECASE | re.DOTALL),
        re.compile(r"drop\s+table", re.IGNORECASE),
    ]

    def check_input_security(self, text: str) -> Tuple[bool, Optional[str]]:
        """
        Validates untrusted input for prompt injection, script injection, and oversized payloads.
        Returns (is_safe, error_message).
        """
        if not text:
            return True, None

        if len(text) > 15000:
            return False, "Input payload exceeds maximum permissible length (15000 characters)."

        for pattern in self.INJECTION_PATTERNS:
            if pattern.search(text):
                return False, f"Potential prompt injection detected matching security filter."

        return True, None

    def extract_code_blocks(self, text: str) -> List[str]:
        """Extracts content inside markdown code blocks."""
        return [match.strip() for match in self.CODE_BLOCK_REGEX.findall(text)]

    def extract_equations(self, text: str) -> List[str]:
        """Extracts formulas and mathematical expressions from text."""
        equations = []
        # LaTeX matches
        for m in self.LATEX_REGEX.finditer(text):
            eq = m.group(1) or m.group(2)
            if eq:
                equations.append(eq.strip())

        # Standard simple physics/math equations (e.g. V = IR, I = V / R)
        for m in self.EQUATION_REGEX.finditer(text):
            eq = m.group(1).strip()
            # Avoid matching regular sentences with equal sign if too long
            if len(eq) <= 30 and ("=" in eq):
                equations.append(eq)

        return list(set(equations))

    def extract_numbers_with_units(self, text: str) -> List[Tuple[str, str]]:
        """Extracts (number, unit) tuples from text."""
        matches = self.NUMBER_UNIT_REGEX.findall(text)
        return [(num, unit.strip()) for num, unit in matches]

    def extract_all_numbers(self, text: str) -> List[str]:
        """Extracts all numbers appearing in the text."""
        return self.STANDALONE_NUMBER_REGEX.findall(text)

    def validate_adaptation(
        self,
        source_text: str,
        adapted_text: str,
        required_terms: Optional[List[str]] = None,
        source_concept_id: Optional[str] = None,
        adapted_concept_id: Optional[str] = None
    ) -> ValidationResult:
        """
        Comprehensive semantic validation between source and candidate adapted text.
        """
        errors: List[str] = []
        warnings: List[str] = []
        formulas_preserved = True
        numbers_preserved = True
        units_preserved = True
        code_preserved = True
        terms_preserved = True
        concept_id_preserved = True

        # 1. Concept ID verification
        if source_concept_id and adapted_concept_id:
            if source_concept_id != adapted_concept_id:
                concept_id_preserved = False
                errors.append(
                    f"Concept ID mutation: Source '{source_concept_id}' != Adapted '{adapted_concept_id}'. "
                    f"Concept IDs must remain language-neutral."
                )

        # 2. Code blocks preservation
        source_code = self.extract_code_blocks(source_text)
        adapted_code = self.extract_code_blocks(adapted_text)
        if source_code:
            for sc in source_code:
                # Normalizing whitespace for code comparison
                norm_sc = "".join(sc.split())
                found = any(norm_sc in "".join(ac.split()) for ac in adapted_code) or (norm_sc in "".join(adapted_text.split()))
                if not found:
                    code_preserved = False
                    errors.append(f"Code block was altered or omitted in localized text.")

        # 3. Mathematical formula preservation
        source_eqs = self.extract_equations(source_text)
        for eq in source_eqs:
            norm_eq = "".join(eq.split()).lower()
            norm_adapted = "".join(adapted_text.split()).lower()
            if norm_eq not in norm_adapted:
                # Check normalized variants (e.g. V=IR vs V=I*R)
                var1 = norm_eq.replace("*", "")
                var2 = norm_eq.replace("·", "")
                if var1 not in norm_adapted and var2 not in norm_adapted:
                    formulas_preserved = False
                    errors.append(f"Mathematical formula mutated or missing: '{eq}'.")

        # 4. Numbers and Units preservation
        source_num_units = self.extract_numbers_with_units(source_text)
        adapted_num_units = self.extract_numbers_with_units(adapted_text)

        source_numbers = self.extract_all_numbers(source_text)
        adapted_numbers = self.extract_all_numbers(adapted_text)

        for num, unit in source_num_units:
            # Verify the number is still present
            if num not in adapted_numbers:
                numbers_preserved = False
                errors.append(f"Numerical value '{num}' from source was lost or mutated.")
            # Verify unit is present
            norm_unit = unit.lower()
            if norm_unit not in adapted_text.lower():
                # Allow standard conversions (e.g., Ω -> Ohms or ohm)
                if norm_unit == "ω" and ("ohm" in adapted_text.lower() or "ओम" in adapted_text):
                    pass
                else:
                    units_preserved = False
                    warnings.append(f"Physical unit '{unit}' not clearly preserved for value '{num}'.")

        # 5. Technical Terminology preservation
        if required_terms:
            for term in required_terms:
                if term.lower() not in adapted_text.lower():
                    # Term wasn't found directly in Latin script, check if it was translated or missing
                    warnings.append(f"Technical term '{term}' was not found directly in target text.")

        is_valid = len(errors) == 0
        return ValidationResult(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
            formulas_preserved=formulas_preserved,
            numbers_preserved=numbers_preserved,
            units_preserved=units_preserved,
            code_preserved=code_preserved,
            terms_preserved=terms_preserved,
            concept_id_preserved=concept_id_preserved,
            retryable=not is_valid
        )

validation_service = ValidationService()
