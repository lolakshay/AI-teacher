"""
Error Codes and Structured Exceptions for Agent 8.
Conforms strictly to Section 42 of the specification.
"""

from enum import Enum
from typing import Optional, Dict, Any

class MultilingualErrorCode(str, Enum):
    UNSUPPORTED_LANGUAGE = "UNSUPPORTED_LANGUAGE"
    TRANSLATION_FAILED = "TRANSLATION_FAILED"
    LANGUAGE_DETECTION_FAILED = "LANGUAGE_DETECTION_FAILED"
    TRANSLATION_VALIDATION_FAILED = "TRANSLATION_VALIDATION_FAILED"
    TERMINOLOGY_CONFLICT = "TERMINOLOGY_CONFLICT"
    CONTEXT_MISSING = "CONTEXT_MISSING"
    PROVIDER_UNAVAILABLE = "PROVIDER_UNAVAILABLE"

class MultilingualException(Exception):
    """Structured exception carrying standardized error payload."""
    def __init__(
        self,
        code: MultilingualErrorCode,
        message: str,
        retryable: bool = False,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.code = code
        self.message = message
        self.retryable = retryable
        self.details = details or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": "failed",
            "error": {
                "code": self.code.value,
                "message": self.message,
                "retryable": self.retryable,
                "details": self.details
            }
        }
