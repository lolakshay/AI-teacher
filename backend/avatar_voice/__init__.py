"""
Avatar + Voice Subsystem (Agent 5) Package.
Provides synthetic human-like teacher presentation: voice synthesis, realistic avatar generation,
timing synchronization, STEM normalization, and integration adapter for Agent 4 (Video Engine).
"""

from backend.avatar_voice.models.voice import (
    VoiceConfig, VoiceStyleType, SpeechSegment, VoiceError
)
from backend.avatar_voice.models.avatar import (
    AvatarConfig, AvatarExpressionType, TeacherGestureType,
    AvatarPositionType, AvatarError
)
from backend.avatar_voice.models.assets import (
    AudioAsset, AvatarAsset, AvatarVoiceSceneResult,
    SceneTiming, AudioSummary, AvatarSummary,
    PresentationMetadata, NormalizedError, FallbackLevel
)

from backend.avatar_voice.processing.speech_normalizer import (
    SpeechNormalizer, speech_normalizer
)
from backend.avatar_voice.processing.speech_segmenter import (
    SpeechSegmenter, speech_segmenter
)
from backend.avatar_voice.processing.timing import (
    TimingSynchronizer, timing_synchronizer
)

from backend.avatar_voice.cache.asset_cache import (
    AssetCache, asset_cache
)

from backend.avatar_voice.providers.base_voice import VoiceProvider
from backend.avatar_voice.providers.mock_voice import MockVoiceProvider
from backend.avatar_voice.providers.external_voice import ExternalVoiceProvider
from backend.avatar_voice.providers.base_avatar import AvatarProvider
from backend.avatar_voice.providers.mock_avatar import MockAvatarProvider
from backend.avatar_voice.providers.external_avatar import ExternalAvatarProvider

from backend.avatar_voice.services.voice_service import (
    VoiceService, voice_service
)
from backend.avatar_voice.services.avatar_service import (
    AvatarService, avatar_service
)
from backend.avatar_voice.services.scene_service import (
    SceneService, scene_service
)

from backend.avatar_voice.api.voice_routes import router as voice_router
from backend.avatar_voice.api.avatar_routes import router as avatar_router

__all__ = [
    # Models
    "VoiceConfig",
    "VoiceStyleType",
    "SpeechSegment",
    "VoiceError",
    "AvatarConfig",
    "AvatarExpressionType",
    "TeacherGestureType",
    "AvatarPositionType",
    "AvatarError",
    "AudioAsset",
    "AvatarAsset",
    "AvatarVoiceSceneResult",
    "SceneTiming",
    "AudioSummary",
    "AvatarSummary",
    "PresentationMetadata",
    "NormalizedError",
    "FallbackLevel",

    # Processing
    "SpeechNormalizer",
    "speech_normalizer",
    "SpeechSegmenter",
    "speech_segmenter",
    "TimingSynchronizer",
    "timing_synchronizer",

    # Cache
    "AssetCache",
    "asset_cache",

    # Providers
    "VoiceProvider",
    "MockVoiceProvider",
    "ExternalVoiceProvider",
    "AvatarProvider",
    "MockAvatarProvider",
    "ExternalAvatarProvider",

    # Services
    "VoiceService",
    "voice_service",
    "AvatarService",
    "avatar_service",
    "SceneService",
    "scene_service",

    # Routers
    "voice_router",
    "avatar_router",
]
