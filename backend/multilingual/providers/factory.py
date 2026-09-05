"""
Provider Factory and Registry.
Supports 'mock', 'llm', and 'auto' selection modes.
"""

from typing import Dict, Optional
from backend.multilingual.providers.base import TranslationProvider
from backend.multilingual.providers.mock_provider import MockTranslationProvider
from backend.multilingual.providers.llm_provider import LLMTranslationProvider
from backend.app.core.config import settings

class TranslationProviderFactory:
    def __init__(self):
        self._mock = MockTranslationProvider()
        self._llm = LLMTranslationProvider(fallback_provider=self._mock)

    def get_provider(self, mode: str = "auto") -> TranslationProvider:
        """
        Returns requested translation provider:
        - 'mock': always uses deterministic offline mock
        - 'llm': always uses LLM provider (falls back to mock if error)
        - 'auto': uses LLM if GEMINI_API_KEY is available, else mock
        """
        mode_clean = mode.lower().strip()
        if mode_clean == "mock":
            return self._mock
        elif mode_clean == "llm":
            return self._llm
        elif mode_clean == "auto":
            return self._llm if settings.GEMINI_API_KEY else self._mock
        return self._mock

provider_factory = TranslationProviderFactory()
