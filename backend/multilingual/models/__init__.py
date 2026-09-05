"""
Multilingual models package exports.
"""

from backend.multilingual.models.language import (
    LanguageConfig,
    LanguageMode,
    SUPPORTED_LANGUAGES,
    DEFAULT_FALLBACK_LANGUAGE,
    normalize_language_code,
    is_supported_language,
    get_language_config
)
from backend.multilingual.models.terminology import (
    TerminologyEntry,
    DisplayPolicy
)
from backend.multilingual.models.adaptation import (
    LanguageAdaptationRequest,
    LanguageSwitchRequest,
    LanguageSwitchResult,
    VisualTextLocalization,
    LanguageDetectionResult,
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

__all__ = [
    "LanguageConfig",
    "LanguageMode",
    "SUPPORTED_LANGUAGES",
    "DEFAULT_FALLBACK_LANGUAGE",
    "normalize_language_code",
    "is_supported_language",
    "get_language_config",
    "TerminologyEntry",
    "DisplayPolicy",
    "LanguageAdaptationRequest",
    "LanguageSwitchRequest",
    "LanguageSwitchResult",
    "VisualTextLocalization",
    "LanguageDetectionResult",
    "ValidationResult",
    "LocalizedTeachingStep",
    "LocalizedQuestion",
    "LocalizedVisualInstruction",
    "LocalizedAssessmentQuestion",
    "MultilingualErrorCode",
    "MultilingualException"
]
