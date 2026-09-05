"""
External Cloud Voice Provider (Agent 5 - Avatar + Voice Engine)
Integrates with external TTS services (OpenAI TTS, ElevenLabs) with bounded retries and graceful error translation.
"""

import time
import httpx
from pathlib import Path
from typing import List, Dict, Any
import uuid

from backend.app.core.config import settings
from backend.avatar_voice.providers.base_voice import VoiceProvider
from backend.avatar_voice.models.assets import AudioAsset
from backend.avatar_voice.models.voice import VoiceConfig, VoiceError
from backend.avatar_voice.processing.timing import timing_synchronizer

class ExternalVoiceProvider(VoiceProvider):
    """
    Adapter for cloud TTS APIs (e.g. OpenAI TTS, ElevenLabs).
    Uses environment variables for authentication.
    """

    def __init__(self, service_type: str = "openai", api_key: str = None):
        self.service_type = service_type.lower()
        self.api_key = api_key or settings.VOICE_API_KEY

    @property
    def provider_name(self) -> str:
        return f"external_{self.service_type}"

    def generate_audio(
        self,
        text: str,
        language: str = "en",
        voice_config: VoiceConfig = None
    ) -> AudioAsset:
        if not self.api_key:
            raise VoiceError(
                f"API Key for {self.service_type} voice provider is not configured.",
                code="VOICE_AUTH_FAILED",
                retryable=False
            )

        config = voice_config or VoiceConfig(language=language)
        asset_id = f"audio_ext_{uuid.uuid4().hex[:8]}"
        out_path = Path(settings.VOICE_CACHE_DIR) / f"{asset_id}.mp3"

        max_retries = getattr(settings, "MAX_PROVIDER_RETRIES", 2)
        last_exception = None

        for attempt in range(max_retries + 1):
            try:
                if self.service_type == "openai":
                    # OpenAI TTS API
                    headers = {
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    }
                    payload = {
                        "model": "tts-1",
                        "input": text,
                        "voice": config.voice_id or "alloy",
                        "speed": config.speaking_rate
                    }
                    with httpx.Client(timeout=15.0) as client:
                        resp = client.post("https://api.openai.com/v1/audio/speech", json=payload, headers=headers)
                        if resp.status_code == 401:
                            raise VoiceError("Unauthorized: Invalid API key", code="VOICE_AUTH_FAILED", retryable=False)
                        if resp.status_code == 400:
                            raise VoiceError(f"Bad Request: {resp.text}", code="VOICE_INVALID_REQUEST", retryable=False)
                        resp.raise_for_status()

                        with open(out_path, "wb") as f:
                            f.write(resp.content)
                elif self.service_type == "elevenlabs":
                    # ElevenLabs API
                    voice_id = config.voice_id or "21m00Tcm4TlvDq8ikWAM"
                    headers = {
                        "xi-api-key": self.api_key,
                        "Content-Type": "application/json"
                    }
                    payload = {
                        "text": text,
                        "model_id": "eleven_multilingual_v2"
                    }
                    with httpx.Client(timeout=15.0) as client:
                        resp = client.post(
                            f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
                            json=payload,
                            headers=headers
                        )
                        if resp.status_code == 401:
                            raise VoiceError("Unauthorized: Invalid ElevenLabs API key", code="VOICE_AUTH_FAILED", retryable=False)
                        resp.raise_for_status()

                        with open(out_path, "wb") as f:
                            f.write(resp.content)
                else:
                    raise VoiceError(f"Unsupported external provider: {self.service_type}", code="VOICE_INVALID_REQUEST")

                # Measure actual audio duration
                duration = timing_synchronizer.get_audio_file_duration(str(out_path))
                if duration <= 0.0:
                    duration = max(1.0, len(text.split()) / 2.5)

                return AudioAsset(
                    asset_id=asset_id,
                    audio_url=f"/api/avatar-voice/assets/audio/{asset_id}",
                    local_path=str(out_path),
                    duration_seconds=duration,
                    language=language,
                    voice_id=config.voice_id or "cloud_voice",
                    sample_rate=24000,
                    format="mp3",
                    provider=self.provider_name,
                    metadata={"provider_type": self.service_type}
                )

            except VoiceError:
                raise
            except Exception as e:
                last_exception = e
                if attempt < max_retries:
                    # Exponential backoff: 0.5s, 1.0s...
                    time.sleep(0.5 * (2 ** attempt))
                else:
                    break

        raise VoiceError(
            f"External voice provider failed after {max_retries} retries: {str(last_exception)}",
            code="VOICE_PROVIDER_UNAVAILABLE",
            retryable=True
        )

    def get_supported_voices(self, language: str = "en") -> List[Dict[str, Any]]:
        return [
            {"voice_id": "alloy", "name": "Alloy", "language": "en"},
            {"voice_id": "echo", "name": "Echo", "language": "en"},
            {"voice_id": "fable", "name": "Fable", "language": "en"},
            {"voice_id": "onyx", "name": "Onyx", "language": "en"},
            {"voice_id": "nova", "name": "Nova", "language": "en"},
            {"voice_id": "shimmer", "name": "Shimmer", "language": "en"}
        ]
