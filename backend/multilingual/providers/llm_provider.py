"""
LLM Translation Provider.
Integrates with the existing LLM service (Gemini) while maintaining
full fallback to MockTranslationProvider in case of API failure or missing keys.
Conforms to Sections 23, 24, 25.
"""

import logging
from typing import Dict, Any, Optional, List
from backend.multilingual.providers.base import TranslationProvider
from backend.multilingual.providers.mock_provider import MockTranslationProvider
from backend.multilingual.prompts.translation_prompt import (
    SYSTEM_PEDAGOGICAL_TRANSLATION_PROMPT,
    build_adaptation_prompt
)
from backend.app.services.llm_service import llm_service
from backend.app.core.config import settings

logger = logging.getLogger(__name__)

class LLMTranslationProvider(TranslationProvider):
    def __init__(self, fallback_provider: Optional[TranslationProvider] = None):
        self.fallback = fallback_provider or MockTranslationProvider()

    def is_available(self) -> bool:
        """Returns whether live LLM credentials are configured."""
        return bool(settings.GEMINI_API_KEY)

    def translate(
        self,
        text: str,
        source_language: str,
        target_language: str,
        context: Optional[Dict[str, Any]] = None,
        terminology: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        if not self.is_available():
            return self.fallback.translate(text, source_language, target_language, context, terminology)

        try:
            prompt = build_adaptation_prompt(
                source_text=text,
                source_language=source_language,
                target_language=target_language,
                terminology=terminology
            )
            fallback_res = self.fallback.translate(text, source_language, target_language, context, terminology)
            fallback_dict = {
                "spoken_text": fallback_res.get("translated_text", text),
                "display_text": text,
                "example": None,
                "preserved_terms": terminology or [],
                "notes": "LLM fallback"
            }

            result = llm_service.generate_json(
                prompt=prompt,
                system_instruction=SYSTEM_PEDAGOGICAL_TRANSLATION_PROMPT,
                fallback_data=fallback_dict
            )

            spoken = result.get("spoken_text") or fallback_res.get("translated_text", text)
            display = result.get("display_text") or spoken

            return {
                "translated_text": spoken,
                "display_text": display,
                "source_language": source_language,
                "target_language": target_language,
                "preserved_terms": result.get("preserved_terms", terminology or [])
            }
        except Exception as e:
            logger.warning(f"LLM translation error: {e}. Falling back to mock provider.")
            return self.fallback.translate(text, source_language, target_language, context, terminology)

    def adapt_teaching_step(
        self,
        source_text: str,
        source_language: str,
        target_language: str,
        topic: Optional[str] = None,
        concept_id: Optional[str] = None,
        learner_level: str = "beginner",
        teaching_style: str = "analogy_driven",
        terminology: Optional[List[str]] = None,
        example: Optional[str] = None
    ) -> Dict[str, Any]:
        if not self.is_available():
            return self.fallback.adapt_teaching_step(
                source_text=source_text,
                source_language=source_language,
                target_language=target_language,
                topic=topic,
                concept_id=concept_id,
                learner_level=learner_level,
                teaching_style=teaching_style,
                terminology=terminology,
                example=example
            )

        try:
            prompt = build_adaptation_prompt(
                source_text=source_text,
                source_language=source_language,
                target_language=target_language,
                topic=topic,
                concept_id=concept_id,
                learner_level=learner_level,
                teaching_style=teaching_style,
                terminology=terminology,
                example=example
            )

            fallback_data = self.fallback.adapt_teaching_step(
                source_text=source_text,
                source_language=source_language,
                target_language=target_language,
                topic=topic,
                concept_id=concept_id,
                learner_level=learner_level,
                teaching_style=teaching_style,
                terminology=terminology,
                example=example
            )

            result = llm_service.generate_json(
                prompt=prompt,
                system_instruction=SYSTEM_PEDAGOGICAL_TRANSLATION_PROMPT,
                fallback_data=fallback_data
            )

            return {
                "spoken_text": result.get("spoken_text", fallback_data["spoken_text"]),
                "display_text": result.get("display_text", fallback_data["display_text"]),
                "example": result.get("example", fallback_data.get("example")),
                "preserved_terms": result.get("preserved_terms", terminology or []),
                "notes": result.get("notes", "LLM-adapted teaching step")
            }
        except Exception as e:
            logger.warning(f"LLM step adaptation error: {e}. Falling back to mock provider.")
            return self.fallback.adapt_teaching_step(
                source_text=source_text,
                source_language=source_language,
                target_language=target_language,
                topic=topic,
                concept_id=concept_id,
                learner_level=learner_level,
                teaching_style=teaching_style,
                terminology=terminology,
                example=example
            )
