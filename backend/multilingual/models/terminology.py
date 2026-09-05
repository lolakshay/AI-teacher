"""
Terminology Data Contracts.
Defines representation and display policies for scientific and technical terms.
"""

from typing import Optional, Literal
from pydantic import BaseModel, Field

DisplayPolicy = Literal[
    "preserve_original",   # Keep original technical term (e.g., 'resistance')
    "localized_only",      # Full translated term (e.g., 'प्रतिरोध')
    "original_only",       # Strictly untranslated regardless of target language
    "bilingual"            # Combined display (e.g., 'resistance (प्रतिरोध)')
]

class TerminologyEntry(BaseModel):
    source_term: str = Field(..., description="Original canonical term (e.g. 'resistance')")
    preferred_term: str = Field(..., description="Target preferred term to use in explanation")
    localized_term: Optional[str] = Field(None, description="Localized equivalent in target language if known")
    display_policy: DisplayPolicy = Field(
        default="preserve_original",
        description="Rendering policy for localized output"
    )
    domain: str = Field(default="general", description="Scientific domain (e.g. physics, circuits, ml, programming)")
    pronunciation_hint: Optional[str] = Field(None, description="Phonetic or pronunciation aid for TTS voice")
    context_hint: Optional[str] = Field(None, description="Pedagogical usage guidance")

    def render_for_language(self, target_lang: str) -> str:
        """Renders term based on display policy and target language."""
        if self.display_policy == "preserve_original" or self.display_policy == "original_only":
            return self.source_term
        if self.display_policy == "localized_only":
            return self.localized_term or self.preferred_term
        if self.display_policy == "bilingual":
            if self.localized_term and self.localized_term.lower() != self.source_term.lower():
                return f"{self.source_term} ({self.localized_term})"
            return self.source_term
        return self.preferred_term
