"""
Voice Provider Interface & Mock Adapter (Agent 4 <-> Agent 5 Handoff)
Conforms to Sections 19, 21, 35, 45 of Agent 4 specification.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from backend.video.schemas import AudioSceneConfig


class VoiceProvider(ABC):
    """Abstract interface for Voice/TTS providers owned by Agent 5."""
    
    @abstractmethod
    def generate_audio(
        self,
        text: str,
        language: str = "Hinglish",
        voice_config: Optional[Dict[str, Any]] = None
    ) -> AudioSceneConfig:
        """
        Generate or synthesize audio for a scene.
        Returns AudioSceneConfig with audio_url and duration_seconds.
        """
        pass


class MockVoiceProvider(VoiceProvider):
    """
    Standard mock provider for hackathon development and testing.
    Estimates natural speaking rate (~140 words per minute / 2.33 words per sec)
    with language-aware metadata preservation.
    """
    def __init__(self, simulate_failure: bool = False):
        self.simulate_failure = simulate_failure

    def generate_audio(
        self,
        text: str,
        language: str = "Hinglish",
        voice_config: Optional[Dict[str, Any]] = None
    ) -> AudioSceneConfig:
        if self.simulate_failure:
            raise RuntimeError("TTS_PROVIDER_UNAVAILABLE")

        clean_text = text.strip() if text else ""
        word_count = len(clean_text.split()) if clean_text else 0
        
        # Approximate 2.33 words per second (140 wpm), minimum 3.0 seconds for short prompts
        computed_duration = max(3.0, round(word_count / 2.33, 1)) if word_count > 0 else 5.0
        
        voice_name = "hi-IN-Neural2-A" if language.lower() in ["hinglish", "hindi"] else "en-US-Neural2-F"
        if voice_config and "voice_name" in voice_config:
            voice_name = voice_config["voice_name"]

        # Synthetic audio asset URL (static or cached)
        audio_slug = f"audio_{abs(hash(clean_text)) % 1000000:06d}.mp3"
        audio_url = f"/static/videos/audio/{audio_slug}"

        return AudioSceneConfig(
            audio_url=audio_url,
            duration_seconds=computed_duration,
            language=language,
            voice_name=voice_name,
            sample_rate=24000
        )
