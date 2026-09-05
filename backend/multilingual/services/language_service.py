"""
Language Management, Language Detection, and Mid-Lesson Switching Service.
Strictly guarantees context preservation during language switching.
Conforms to Sections 7, 32, 33, 35, 36.
"""

import re
import logging
from typing import Optional, Dict, Any, List
from backend.multilingual.models.language import (
    normalize_language_code,
    is_supported_language,
    SUPPORTED_LANGUAGES,
    DEFAULT_FALLBACK_LANGUAGE
)
from backend.multilingual.models.adaptation import (
    LanguageDetectionResult,
    LanguageSwitchResult,
    LanguageSwitchRequest
)
from backend.multilingual.models.errors import (
    MultilingualErrorCode,
    MultilingualException
)
from backend.multilingual.services.translation_service import translation_service
from backend.app.services.orchestrator import orchestrator

logger = logging.getLogger(__name__)

class LanguageService:
    # Common Hinglish marker words written in Latin script
    HINGLISH_MARKERS = {
        "hai", "hain", "karta", "karte", "karti", "hoga", "hogi", "hoge",
        "badhta", "badhega", "kam", "ghatega", "mein", "aur", "toh", "kaise",
        "aaj", "hum", "chaliye", "roop", "beech", "samajh", "samjhenge", "samajhte",
        "zahir", "si", "baat", "paani", "rakh", "dein", "isliye", "hamesha",
        "batayiye", "jisse", "bohot", "ek", "se", "ko", "par", "kya", "hota"
    }

    # Regex for Devanagari unicode range (U+0900 to U+097F)
    DEVANAGARI_REGEX = re.compile(r"[\u0900-\u097F]")

    def detect_language(self, text: str) -> LanguageDetectionResult:
        """
        Detects language of input text (English, Hindi, Hinglish).
        Conforms to Section 35.
        """
        if not text or not text.strip():
            return LanguageDetectionResult(
                language="en",
                confidence=1.0,
                script="Latin",
                is_mixed=False
            )

        clean = text.strip()

        # Check for Devanagari script (Native Hindi)
        devanagari_chars = len(self.DEVANAGARI_REGEX.findall(clean))
        total_letters = sum(1 for c in clean if c.isalpha())

        if total_letters > 0 and (devanagari_chars / total_letters) > 0.3:
            conf = min(0.99, max(0.6, (devanagari_chars / total_letters) + 0.2))
            return LanguageDetectionResult(
                language="hi",
                confidence=round(conf, 2),
                script="Devanagari",
                is_mixed=False
            )

        # Check for Hinglish markers in Latin text
        words = [w.lower().strip(".,!?:;\"'()") for w in clean.split()]
        matched_markers = [w for w in words if w in self.HINGLISH_MARKERS]

        if len(matched_markers) >= 2 or (len(words) <= 5 and len(matched_markers) >= 1):
            ratio = len(matched_markers) / max(1, len(words))
            conf = min(0.98, max(0.7, 0.6 + ratio * 0.4))
            return LanguageDetectionResult(
                language="hi-en",
                confidence=round(conf, 2),
                script="Latin",
                is_mixed=True,
                detected_markers=matched_markers
            )

        # Default to English for Latin text with no strong Hindi markers
        return LanguageDetectionResult(
            language="en",
            confidence=0.92,
            script="Latin",
            is_mixed=False
        )

    def resolve_language(
        self,
        session_language: Optional[str] = None,
        profile_language: Optional[str] = None
    ) -> str:
        """
        Resolves language priority:
        1. Explicit session language
        2. Student profile language
        3. Application default ('en')
        """
        if session_language and is_supported_language(session_language):
            return normalize_language_code(session_language)
        if profile_language and is_supported_language(profile_language):
            return normalize_language_code(profile_language)
        return DEFAULT_FALLBACK_LANGUAGE

    def switch_session_language(
        self,
        session_id: str,
        target_language: str,
        teaching_style: Optional[str] = None
    ) -> LanguageSwitchResult:
        """
        Switches session teaching language WITHOUT restarting the lesson!
        Strictly preserves:
        - Topic
        - Concept
        - Lesson plan position (current_step_index)
        - Student profile & learner level
        - Misconceptions & active evaluations
        - Assessment state
        """
        session = orchestrator.get_session(session_id)
        if not session:
            raise MultilingualException(
                code=MultilingualErrorCode.CONTEXT_MISSING,
                message=f"Active session '{session_id}' not found."
            )

        target_norm = normalize_language_code(target_language)
        prev_lang = session.learning_request.preferred_language or "en"

        # Update language on session
        session.learning_request.preferred_language = target_norm
        if session.student_profile:
            session.student_profile.preferred_language = target_norm

        current_step = orchestrator.get_current_step(session_id)
        localized_step_dict = None

        if current_step:
            # Re-adapt current step to new language
            style = teaching_style or session.learning_request.teaching_style or "analogy_driven"
            localized_step = translation_service.adapt_teaching_step(
                step=current_step,
                target_language=target_norm,
                teaching_style=style
            )
            # Update step in session memory so subsequent requests get localized version
            current_step.language = target_norm
            current_step.explanation = localized_step.spoken_text
            if localized_step.example and hasattr(current_step, "example"):
                current_step.example = localized_step.example
            if localized_step.question and current_step.question:
                current_step.question.prompt = localized_step.question.localized_text

            localized_step_dict = localized_step.model_dump()

        logger.info(
            f"Session {session_id}: Switched language from {prev_lang} to {target_norm}. "
            f"Concept '{session.current_concept}' at step {session.current_step_index} preserved."
        )

        return LanguageSwitchResult(
            session_id=session_id,
            previous_language=prev_lang,
            current_language=target_norm,
            current_concept=session.current_concept or (session.lesson_plan.topic if session.lesson_plan else ""),
            lesson_position=session.current_step_index,
            total_steps=len(session.steps) if session.steps else 0,
            localized_current_step=localized_step_dict,
            status="success",
            message=f"Language switched to {target_norm} seamlessly without lesson restart."
        )

language_service = LanguageService()
