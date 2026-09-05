"""
Abstract Base Class for Avatar Video Providers (Agent 5 - Avatar + Voice Engine)
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from backend.avatar_voice.models.assets import AvatarAsset, AudioAsset
from backend.avatar_voice.models.avatar import AvatarConfig

class AvatarProvider(ABC):
    """
    Abstract interface for synthetic teacher avatar video generators.
    """

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Returns the canonical name of the provider."""
        pass

    @abstractmethod
    def generate_avatar_scene(
        self,
        spoken_text: str,
        audio_asset: AudioAsset,
        language: str = "en",
        avatar_config: Optional[AvatarConfig] = None,
        expression: str = "friendly",
        duration: Optional[float] = None
    ) -> AvatarAsset:
        """
        Generates teacher avatar video matching the spoken text and audio timing.
        """
        pass

    @abstractmethod
    def get_supported_avatars(self) -> List[Dict[str, Any]]:
        """
        Returns list of available avatar personas and capabilities.
        """
        pass
