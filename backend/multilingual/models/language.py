"""
Language Configuration and Registry Data Contracts.
Defines supported languages, scripts, modes, and normalization rules.
"""

from typing import List, Dict, Optional, Literal
from pydantic import BaseModel, Field

LanguageMode = Literal["native", "translated", "mixed"]

class LanguageConfig(BaseModel):
    language_code: str = Field(..., description="ISO 639-1 or composite code (e.g., 'en', 'hi', 'hi-en')")
    language_name: str = Field(..., description="Full readable name (e.g., 'English', 'Hindi', 'Hinglish')")
    script: str = Field(default="Latin", description="Writing script (e.g., 'Latin', 'Devanagari')")
    mode: LanguageMode = Field(default="native", description="Teaching mode: native, translated, or mixed")
    is_default: bool = False
    supported_styles: List[str] = Field(
        default_factory=lambda: ["simple", "analogy_driven", "technical", "conversational", "exam-focused"]
    )
    aliases: List[str] = Field(default_factory=list)

# Supported languages in accordance with project requirements
SUPPORTED_LANGUAGES: Dict[str, LanguageConfig] = {
    "en": LanguageConfig(
        language_code="en",
        language_name="English",
        script="Latin",
        mode="native",
        is_default=True,
        aliases=["english", "eng", "en-us", "en-in"]
    ),
    "hi": LanguageConfig(
        language_code="hi",
        language_name="Hindi",
        script="Devanagari",
        mode="native",
        is_default=False,
        aliases=["hindi", "hin", "hi-in"]
    ),
    "hi-en": LanguageConfig(
        language_code="hi-en",
        language_name="Hinglish",
        script="Latin",
        mode="mixed",
        is_default=False,
        aliases=["hinglish", "hindi-english", "mixed-hindi", "hi_en"]
    )
}

DEFAULT_FALLBACK_LANGUAGE = "en"

def normalize_language_code(language_identifier: str) -> str:
    """
    Normalizes any language string, alias, or code to a canonical supported code.
    E.g.: 'Hinglish' -> 'hi-en', 'Hindi' -> 'hi', 'en-US' -> 'en'.
    Returns 'en' if not recognized.
    """
    if not language_identifier:
        return DEFAULT_FALLBACK_LANGUAGE

    clean = language_identifier.strip().lower().replace("_", "-")

    # Direct match on code
    if clean in SUPPORTED_LANGUAGES:
        return clean

    # Alias match
    for code, config in SUPPORTED_LANGUAGES.items():
        if clean == code or clean in [a.lower() for a in config.aliases] or clean == config.language_name.lower():
            return code

    # Partial / subtag match
    if clean.startswith("hi-") or "hinglish" in clean:
        return "hi-en"
    if clean.startswith("hi"):
        return "hi"
    if clean.startswith("en"):
        return "en"

    return DEFAULT_FALLBACK_LANGUAGE

def is_supported_language(language_identifier: str) -> bool:
    """Checks if the given language code or name is officially supported."""
    if not language_identifier:
        return False
    clean = language_identifier.strip().lower().replace("_", "-")
    for code, config in SUPPORTED_LANGUAGES.items():
        if clean == code or clean in [a.lower() for a in config.aliases] or clean == config.language_name.lower():
            return True
    return False

def get_language_config(language_identifier: str) -> LanguageConfig:
    """Returns the LanguageConfig for a given language identifier, with fallback to default."""
    code = normalize_language_code(language_identifier)
    return SUPPORTED_LANGUAGES.get(code, SUPPORTED_LANGUAGES[DEFAULT_FALLBACK_LANGUAGE])
