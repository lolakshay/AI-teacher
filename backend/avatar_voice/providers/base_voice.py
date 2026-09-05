"""
Abstract Base Class for Voice / TTS Providers (Agent 5 - Avatar + Voice Engine)
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any
from backend.avatar_voice.models.assets import AudioAsset
from backend.avatar_voice.models.voice import VoiceConfig

class VoiceProvider(ABC):
    """
    Abstract interface for Text-to-Speech synthesis providers.
    Follows provider-agnostic architecture.
    """

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Returns the canonical name of the provider."""
        pass

    @abstractmethod
    def generate_audio(
        self,
        text: str,
        language: str = "en",
        voice_config: VoiceConfig = None
    ) -> AudioAsset:
        """
        Synthesizes spoken speech from text.
        Must return a valid AudioAsset with accurate duration.
        """
        pass

    @abstractmethod
    def get_supported_voices(self, language: str = "en") -> List[Dict[str, Any]]:
        """
        Returns a list of supported voices for the requested language.
        """
        pass
