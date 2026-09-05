"""
Provider abstractions and mock implementations for Voice and Avatar.
"""

from backend.video.providers.voice_provider import VoiceProvider, MockVoiceProvider
from backend.video.providers.avatar_provider import AvatarProvider, MockAvatarProvider

__all__ = [
    "VoiceProvider",
    "MockVoiceProvider",
    "AvatarProvider",
    "MockAvatarProvider"
]
