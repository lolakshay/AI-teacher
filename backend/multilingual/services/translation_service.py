"""
Core Translation and Educational Adaptation Service.
Orchestrates caching, security validation, terminology protection, provider execution,
semantic validation, and fallback handling.
Conforms to Sections 8, 9, 10, 11, 16, 17, 19, 20, 21, 22, 26, 42.
"""

import logging
from typing import Dict, Any, Optional, List
from backend.multilingual.models.language import (
    normalize_language_code,
    is_supported_language,
    DEFAULT_FALLBACK_LANGUAGE
)
from backend.multilingual.models.adaptation import (
    LanguageAdaptationRequest,
    VisualTextLocalization,
    ValidationResult
)
from backend.multilingual.models.localized_step import (
    LocalizedTeachingStep,
    LocalizedQuestion,
    LocalizedVisualInstruction,
    LocalizedAssessmentQuestion
)
from backend.multilingual.models.errors import (
    MultilingualErrorCode,
    MultilingualException
)
from backend.multilingual.services.cache_service import cache_service
from backend.multilingual.services.validation_service import validation_service
from backend.multilingual.services.terminology_service import terminology_service
from backend.multilingual.providers.factory import provider_factory
from backend.app.core.models import TeachingStep, QuestionPayload

logger = logging.getLogger(__name__)

class TranslationService:
    def __init__(self, provider_mode: str = "auto"):
        self.provider = provider_factory.get_provider(provider_mode)

    # Dictionary of standard visual labels for circuits/math
    VISUAL_LABEL_MAP = {
        "Voltage": {"hi": "वोल्टेज (V)", "hi-en": "Voltage (V)", "en": "Voltage (V)"},
        "Current": {"hi": "करंट (I)", "hi-en": "Current (I)", "en": "Current (I)"},
        "Resistance": {"hi": "प्रतिरोध (R)", "hi-en": "Resistance (R)", "en": "Resistance (R)"},
        "Power": {"hi": "शक्ति (P)", "hi-en": "Power (P)", "en": "Power (P)"},
        "Electrons": {"hi": "इलेक्ट्रॉन्स", "hi-en": "Electrons", "en": "Electrons"},
        "Battery": {"hi": "बैटरी", "hi-en": "Battery", "en": "Battery"},
        "Switch": {"hi": "स्विच", "hi-en": "Switch", "en": "Switch"},
    }

    def adapt_text(self, request: LanguageAdaptationRequest) -> Dict[str, Any]:
        """Adapts arbitrary educational text according to pedagogical requirements."""
        # 1. Security check
        is_safe, sec_err = validation_service.check_input_security(request.source_text)
        if not is_safe:
            raise MultilingualException(
                code=MultilingualErrorCode.TRANSLATION_FAILED,
                message=f"Security rejection: {sec_err}",
                retryable=False
            )

        # 2. Language validation & fallback
        src_lang = normalize_language_code(request.source_language)
        requested_target = request.target_language
        is_supported = is_supported_language(requested_target)
        target_lang = normalize_language_code(requested_target) if is_supported else DEFAULT_FALLBACK_LANGUAGE

        # Fast path: same language requested or fell back to same source language
        if src_lang == target_lang:
            return {
                "status": "ready" if is_supported else "unsupported_language_fallback",
                "requested_language": requested_target,
                "language": target_lang,
                "source_language": src_lang,
                "spoken_text": request.source_text,
                "display_text": request.source_text,
                "concept_id": request.concept_id,
                "preserved_terms": request.terminology_hints,
                "validation": {
                    "is_valid": True,
                    "formulas_preserved": True,
                    "numbers_preserved": True,
                    "units_preserved": True,
                    "code_preserved": True,
                    "terms_preserved": True,
                    "concept_id_preserved": True,
                    "errors": [],
                    "warnings": []
                },
                "cached": False
            }

        # 3. Check Cache
        cache_key = cache_service.generate_cache_key(
            source_text=request.source_text,
            source_language=src_lang,
            target_language=target_lang,
            terminology=request.terminology_hints,
            teaching_style=request.teaching_style,
            learner_level=request.learner_level
        )
        cached_result = cache_service.get(cache_key)
        if cached_result:
            return {
                **cached_result,
                "cached": True,
                "status": "ready" if is_supported else "unsupported_language_fallback"
            }

        # 4. Adapt using provider with raw source text
        adaptation_output = self.provider.adapt_teaching_step(
            source_text=request.source_text,
            source_language=src_lang,
            target_language=target_lang,
            topic=request.topic,
            concept_id=request.concept_id,
            learner_level=request.learner_level,
            teaching_style=request.teaching_style,
            terminology=request.terminology_hints
        )

        spoken_restored = adaptation_output["spoken_text"]
        display_restored = adaptation_output.get("display_text", spoken_restored)

        # 5. Semantic Validation (Check equations, code, numbers, units)
        validation = validation_service.validate_adaptation(

            source_text=request.source_text,
            adapted_text=spoken_restored,
            required_terms=request.terminology_hints,
            source_concept_id=request.concept_id,
            adapted_concept_id=request.concept_id
        )

        if not validation.is_valid:
            logger.warning(f"Validation failure for '{request.source_text}': {validation.errors}")
            # If formulas or numbers were damaged, prioritize display preservation
            if not validation.formulas_preserved or not validation.numbers_preserved:
                display_restored = request.source_text

        result_payload = {
            "status": "ready" if is_supported else "unsupported_language_fallback",
            "requested_language": requested_target,
            "language": target_lang,
            "source_language": src_lang,
            "spoken_text": spoken_restored,
            "display_text": display_restored,
            "concept_id": request.concept_id,
            "preserved_terms": adaptation_output.get("preserved_terms", []) or request.terminology_hints,
            "validation": validation.model_dump(),
            "cached": False
        }

        # 8. Cache valid result
        if validation.is_valid:
            cache_service.set(cache_key, result_payload)

        return result_payload

    def adapt_teaching_step(
        self,
        step: TeachingStep,
        target_language: str,
        teaching_style: str = "analogy_driven"
    ) -> LocalizedTeachingStep:
        """
        Transforms a complete TeachingStep into a LocalizedTeachingStep
        consumable by Agent 4 (Video) and Agent 5 (Voice).
        Strict invariant: concept_id remains language-neutral!
        """
        req = LanguageAdaptationRequest(
            session_id=None,
            teaching_step_id=step.step_id,
            source_text=step.explanation,
            source_language=step.language or "en",
            target_language=target_language,
            concept_id=step.concept_id,
            learner_level=step.difficulty or "beginner",
            teaching_style=teaching_style
        )
        adaptation_res = self.adapt_text(req)

        # Adapt example if present
        localized_example = None
        if step.example:
            ex_req = LanguageAdaptationRequest(
                source_text=step.example,
                source_language=step.language or "en",
                target_language=target_language,
                concept_id=step.concept_id,
                learner_level=step.difficulty or "beginner",
                teaching_style=teaching_style
            )
            ex_res = self.adapt_text(ex_req)
            localized_example = ex_res["spoken_text"]

        # Adapt question if present
        localized_question = None
        if step.question:
            localized_question = self.adapt_question(
                question=step.question,
                target_language=target_language,
                concept_id=step.concept_id
            )

        # Adapt visual instruction if present
        localized_visual = None
        if step.visual_instruction:
            v_data = step.visual_instruction.data if hasattr(step.visual_instruction, "data") else {}
            # Generate localized labels for video renderer
            labels_map = {}
            for term in ["Voltage", "Current", "Resistance", "Power"]:
                if term in self.VISUAL_LABEL_MAP:
                    tgt_norm = normalize_language_code(target_language)
                    labels_map[term] = self.VISUAL_LABEL_MAP[term].get(tgt_norm, term)

            localized_visual = LocalizedVisualInstruction(
                type=step.visual_instruction.type,
                title=step.visual_instruction.title,
                caption=step.visual_instruction.caption,
                labels=labels_map,
                data=v_data  # numerical parameters remain untouched!
            )

        return LocalizedTeachingStep(
            teaching_step_id=step.step_id,
            concept_id=step.concept_id,  # Strictly language-neutral!
            source_language=step.language or "en",
            teaching_language=normalize_language_code(target_language),
            canonical_text=step.explanation,
            spoken_text=adaptation_res["spoken_text"],
            display_text=adaptation_res["display_text"],
            example=localized_example,
            terminology=adaptation_res.get("preserved_terms", []),
            visual_instruction=localized_visual,
            question=localized_question,
            source_references=step.source_references or [],
            metadata={
                "avatar_emotion": step.avatar_emotion,
                "step_type": step.step_type,
                "learner_level": step.difficulty
            }
        )

    def adapt_question(
        self,
        question: QuestionPayload,
        target_language: str,
        concept_id: str
    ) -> LocalizedQuestion:
        """Localizes question while preserving canonical prompt and expected concept."""
        q_text = question.prompt if hasattr(question, "prompt") else getattr(question, "question_text", "")
        tgt_norm = normalize_language_code(target_language)

        # Adapt question prompt
        req = LanguageAdaptationRequest(
            source_text=q_text,
            source_language="en",
            target_language=tgt_norm,
            concept_id=concept_id
        )
        adapted = self.adapt_text(req)

        # Adapt hints if any
        localized_hints = []
        if hasattr(question, "hints") and question.hints:
            for hint in question.hints:
                h_req = LanguageAdaptationRequest(
                    source_text=hint,
                    source_language="en",
                    target_language=tgt_norm,
                    concept_id=concept_id
                )
                h_res = self.adapt_text(h_req)
                localized_hints.append(h_res["spoken_text"])

        return LocalizedQuestion(
            question_id=question.question_id,
            canonical_text=q_text,
            localized_text=adapted["spoken_text"],
            language=tgt_norm,
            expected_concept=concept_id,
            options=getattr(question, "options", None),
            hints=localized_hints,
            question_type=getattr(question, "question_type", "conceptual_check"),
            pedagogical_goal=getattr(question, "pedagogical_goal", None)
        )

    def adapt_assessment_question(
        self,
        question: QuestionPayload,
        target_language: str,
        expected_concept: str
    ) -> LocalizedAssessmentQuestion:
        """Adapts an assessment question for Agent 7."""
        q_text = question.prompt if hasattr(question, "prompt") else getattr(question, "question_text", "")
        tgt_norm = normalize_language_code(target_language)

        req = LanguageAdaptationRequest(
            source_text=q_text,
            source_language="en",
            target_language=tgt_norm,
            concept_id=expected_concept
        )
        adapted = self.adapt_text(req)

        return LocalizedAssessmentQuestion(
            question_id=question.question_id,
            canonical_text=q_text,
            localized_text=adapted["spoken_text"],
            language=tgt_norm,
            expected_concept=expected_concept,
            expected_answer=getattr(question, "expected_answer", None),
            options=getattr(question, "options", None),
            hints=getattr(question, "hints", [])
        )

    def localize_visual_labels(
        self,
        labels: List[str],
        target_language: str
    ) -> List[VisualTextLocalization]:
        """Localizes visual labels for Agent 4 video engine."""
        tgt = normalize_language_code(target_language)
        results = []
        for lbl in labels:
            clean = lbl.strip()
            if clean in self.VISUAL_LABEL_MAP:
                loc_text = self.VISUAL_LABEL_MAP[clean].get(tgt, clean)
            else:
                loc_text = clean
            results.append(VisualTextLocalization(
                source=clean,
                localized=loc_text,
                preserve_original=True
            ))
        return results

translation_service = TranslationService()
