"""
Avatar Provider Interface & Mock Adapter (Agent 4 <-> Agent 5 Handoff)
Conforms to Sections 18, 21, 30, 45 of Agent 4 specification.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from backend.video.schemas import AvatarSceneConfig


class AvatarProvider(ABC):
    """Abstract interface for Avatar animation/render providers owned by Agent 5."""
    
    @abstractmethod
    def generate_avatar_scene(
        self,
        spoken_text: str,
        duration: float,
        language: str = "Hinglish",
        expression: str = "explaining",
        position: str = "right"
    ) -> AvatarSceneConfig:
        """
        Generate avatar animation asset or stream reference.
        Returns AvatarSceneConfig with asset_url, duration, expression, and position.
        """
        pass


class MockAvatarProvider(AvatarProvider):
    """
    Standard mock avatar provider for development and testing.
    Produces high-fidelity avatar asset references without blocking pipeline.
    """
    def __init__(self, simulate_failure: bool = False):
        self.simulate_failure = simulate_failure

    def generate_avatar_scene(
        self,
        spoken_text: str,
        duration: float,
        language: str = "Hinglish",
        expression: str = "explaining",
        position: str = "right"
    ) -> AvatarSceneConfig:
        if self.simulate_failure:
            raise RuntimeError("AVATAR_PROVIDER_UNAVAILABLE")

        # Map position to appropriate scale (smaller for equations/complex visual scenes)
        scale = 1.0
        if position == "small" or position == "bottom_right":
            scale = 0.65
        elif position == "hidden":
            scale = 0.0

        avatar_slug = f"avatar_{expression}_{position}.webm"
        asset_url = f"/static/videos/avatar/{avatar_slug}"

        return AvatarSceneConfig(
            visible=(position != "hidden"),
            expression=expression,
            position=position,
            scale=scale,
            asset_url=asset_url,
            duration_seconds=duration
        )
