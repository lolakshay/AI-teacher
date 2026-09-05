"""
Voice Service Orchestration Layer (Agent 5 - Avatar + Voice Engine)
Orchestrates speech normalization, segmentation, provider dispatch, caching, and timing calibration.
"""

from typing import Dict, Any, Optional, List
from backend.app.core.config import settings
from backend.avatar_voice.models.assets import AudioAsset
from backend.avatar_voice.models.voice import VoiceConfig, SpeechSegment, VoiceError
from backend.avatar_voice.providers.base_voice import VoiceProvider
from backend.avatar_voice.providers.mock_voice import MockVoiceProvider
from backend.avatar_voice.providers.external_voice import ExternalVoiceProvider
from backend.avatar_voice.processing.speech_normalizer import speech_normalizer
from backend.avatar_voice.processing.speech_segmenter import speech_segmenter
from backend.avatar_voice.cache.asset_cache import asset_cache

class VoiceService:
    """
    Core service managing text-to-speech generation, phonetic normalization, and caching.
    """

    def __init__(self):
        self._providers: Dict[str, VoiceProvider] = {
            "mock": MockVoiceProvider(),
            "openai": ExternalVoiceProvider("openai"),
            "elevenlabs": ExternalVoiceProvider("elevenlabs")
        }

    def register_provider(self, name: str, provider: VoiceProvider) -> None:
        """Dynamically registers or overrides a voice provider."""
        self._providers[name.lower()] = provider

    def get_provider(self, name: Optional[str] = None) -> VoiceProvider:
        """Resolves active provider based on request, config, or fallback to mock."""
        target = (name or getattr(settings, "VOICE_PROVIDER", "mock")).lower()
        if target in self._providers:
            return self._providers[target]
        # Safe fallback to mock provider
        return self._providers["mock"]

    def synthesize(
        self,
        raw_text: str,
        language: str = "en",
        voice_config: Optional[VoiceConfig] = None
    ) -> Dict[str, Any]:
        """
        Full TTS pipeline:
        1. Normalizes display_text -> spoken_text (equations, LaTeX, units).
        2. Computes stable SHA-256 cache key.
        3. Checks asset cache.
        4. Synthesizes via configured provider if cache miss.
        5. Performs speech segmentation with accurate timing.
        6. Caches and returns result.
        """
        config = voice_config or VoiceConfig(language=language)
        provider = self.get_provider(config.provider)

        # 1. Normalization
        display_text, spoken_text = speech_normalizer.normalize(raw_text, language=language)

        # 2. Check Cache
        cache_key = asset_cache.compute_voice_key(
            normalized_text=spoken_text,
            language=language,
            voice_id=config.voice_id,
            speaking_rate=config.speaking_rate,
            pitch=config.pitch,
            provider=provider.provider_name
        )

        cached_asset = asset_cache.get_voice(cache_key)
        if cached_asset:
            segments = speech_segmenter.segment(
                spoken_text,
                total_duration=cached_asset.duration_seconds,
                speaking_rate=config.speaking_rate
            )
            return {
                "audio_asset": cached_asset,
                "segments": segments,
                "display_text": display_text,
                "spoken_text": spoken_text,
                "cache_hit": True
            }

        # 3. Generate Audio
        try:
            audio_asset = provider.generate_audio(
                text=spoken_text,
                language=language,
                voice_config=config
            )
        except VoiceError:
            raise
        except Exception as e:
            raise VoiceError(f"Unexpected voice synthesis failure: {str(e)}", code="VOICE_GENERATION_FAILED", retryable=True)

        # 4. Generate Segments
        segments = speech_segmenter.segment(
            spoken_text,
            total_duration=audio_asset.duration_seconds,
            speaking_rate=config.speaking_rate
        )

        # 5. Store in Cache
        asset_cache.put_voice(cache_key, audio_asset)

        return {
            "audio_asset": audio_asset,
            "segments": segments,
            "display_text": display_text,
            "spoken_text": spoken_text,
            "cache_hit": False
        }

    def get_supported_voices(self, language: str = "en") -> List[Dict[str, Any]]:
        provider = self.get_provider()
        return provider.get_supported_voices(language)

voice_service = VoiceService()
