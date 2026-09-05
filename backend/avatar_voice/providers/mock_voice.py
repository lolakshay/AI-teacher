"""
Deterministic Mock Voice Provider (Agent 5 - Avatar + Voice Engine)
Synthesizes real PCM WAV audio using Python's standard library.
Ensures genuine file headers, accurate duration, and zero external API dependencies.
"""

import wave
import struct
import math
from pathlib import Path
from typing import List, Dict, Any
import uuid

from backend.app.core.config import settings
from backend.avatar_voice.providers.base_voice import VoiceProvider
from backend.avatar_voice.models.assets import AudioAsset
from backend.avatar_voice.models.voice import VoiceConfig

class MockVoiceProvider(VoiceProvider):
    """
    Standard mock TTS generator.
    Creates valid 24kHz 16-bit PCM WAV audio files locally with speech-like modulation.
    """

    @property
    def provider_name(self) -> str:
        return "mock"

    def generate_audio(
        self,
        text: str,
        language: str = "en",
        voice_config: VoiceConfig = None
    ) -> AudioAsset:
        config = voice_config or VoiceConfig(language=language)
        
        # Calculate realistic pedagogical speech duration (~2.5 words/sec adjusted for rate)
        words = text.split()
        word_count = max(1, len(words))
        speaking_rate = max(0.5, config.speaking_rate)
        # Add slight base duration for pauses and sentence delivery
        duration = max(1.2, round(word_count / (2.4 * speaking_rate), 2))

        sample_rate = 24000
        num_samples = int(sample_rate * duration)

        # Output path
        asset_id = f"audio_mock_{uuid.uuid4().hex[:8]}"
        out_dir = Path(settings.VOICE_CACHE_DIR)
        out_dir.mkdir(parents=True, exist_ok=True)
        file_path = out_dir / f"{asset_id}.wav"

        # Pitch modulation frequency (base 220Hz + config.pitch)
        base_freq = max(100.0, 220.0 + (config.pitch * 5.0))
        volume = max(0.1, min(1.0, config.volume)) * 0.25  # Soft pleasant tone

        # Write valid PCM WAV file
        with wave.open(str(file_path), "wb") as wf:
            wf.setnchannels(1)  # Mono
            wf.setsampwidth(2)  # 16-bit
            wf.setframerate(sample_rate)

            # Generate cadence-modulated waveform simulating human speech envelope
            frames = bytearray()
            for i in range(num_samples):
                t = float(i) / sample_rate
                # Low frequency envelope (syllabic rhythm ~ 4Hz)
                envelope = 0.5 * (1.0 + math.sin(2.0 * math.pi * 4.0 * t))
                # Acoustic carrier wave
                val = math.sin(2.0 * math.pi * base_freq * t) * envelope * volume
                # Quantize to 16-bit signed integer
                sample = int(max(-32767, min(32767, val * 32767.0)))
                frames.extend(struct.pack("<h", sample))

            wf.writeframes(frames)

        return AudioAsset(
            asset_id=asset_id,
            audio_url=f"/api/avatar-voice/assets/audio/{asset_id}",
            local_path=str(file_path),
            duration_seconds=duration,
            language=language,
            voice_id=config.voice_id or f"mock_teacher_{language}",
            sample_rate=sample_rate,
            format="wav",
            provider=self.provider_name,
            metadata={
                "speaking_rate": config.speaking_rate,
                "pitch": config.pitch,
                "style": config.style,
                "word_count": word_count,
                "simulated": True
            }
        )

    def get_supported_voices(self, language: str = "en") -> List[Dict[str, Any]]:
        return [
            {
                "voice_id": f"mock_{language}_teacher_female",
                "name": f"Teacher Maya ({language.capitalize()})",
                "gender": "female",
                "language": language,
                "style_support": ["friendly", "encouraging", "patient"]
            },
            {
                "voice_id": f"mock_{language}_teacher_male",
                "name": f"Teacher Rohan ({language.capitalize()})",
                "gender": "male",
                "language": language,
                "style_support": ["professional", "conversational", "curious"]
            }
        ]
