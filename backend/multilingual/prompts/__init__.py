"""
Multilingual prompts package exports.
"""

from backend.multilingual.prompts.translation_prompt import (
    SYSTEM_PEDAGOGICAL_TRANSLATION_PROMPT,
    build_adaptation_prompt
)

__all__ = [
    "SYSTEM_PEDAGOGICAL_TRANSLATION_PROMPT",
    "build_adaptation_prompt"
]
