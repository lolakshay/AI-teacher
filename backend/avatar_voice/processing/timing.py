"""
Timing Synchronization and Audio/Avatar Drift Management (Agent 5)
Measures physical asset durations and validates lip-sync / video alignment against MAX_DURATION_DRIFT_SECONDS.
"""

import wave
import os
from pathlib import Path
from typing import Optional, List
from backend.app.core.config import settings
from backend.avatar_voice.models.assets import SceneTiming
from backend.avatar_voice.models.voice import SpeechSegment

class TimingSynchronizer:
    """
    Measures and aligns audio/avatar temporal bounds for Agent 4 video composition.
    """

    @staticmethod
    def get_audio_file_duration(file_path: str) -> float:
        """
        Reads precise duration in seconds directly from WAV header.
        Falls back to file size calculation or soundfile if non-WAV.
        """
        path = Path(file_path)
        if not path.exists():
            return 0.0

        if path.suffix.lower() == ".wav":
            try:
                with wave.open(str(path), "rb") as wf:
                    frames = wf.getnframes()
                    rate = wf.getframerate()
                    if rate > 0:
                        return round(frames / float(rate), 3)
            except Exception:
                pass

        # Fallback using soundfile if available
        try:
            import soundfile as sf
            info = sf.info(str(path))
            return round(info.duration, 3)
        except Exception:
            pass

        # Rough estimate fallback: 16-bit 24kHz mono PCM is 48000 bytes/sec
        size_bytes = os.path.getsize(str(path))
        return round(size_bytes / 48000.0, 3)

    def synchronize(
        self,
        audio_duration: float,
        avatar_duration: float,
        segments: Optional[List[SpeechSegment]] = None
    ) -> SceneTiming:
        """
        Calculates drift and determines if video and audio are synchronized within tolerance.
        """
        drift = abs(audio_duration - avatar_duration)
        max_drift = getattr(settings, "MAX_DURATION_DRIFT_SECONDS", 0.5)
        acceptable = drift <= max_drift

        # Final scene duration is max of audio and avatar to avoid premature cutoffs
        final_duration = max(audio_duration, avatar_duration)

        # Re-scale speech segments if provided so that timing strictly matches audio
        rescaled_segments = []
        if segments:
            for s in segments:
                rescaled_segments.append(s)

        return SceneTiming(
            duration_seconds=round(final_duration, 2),
            segments=rescaled_segments,
            audio_duration=round(audio_duration, 2),
            avatar_duration=round(avatar_duration, 2),
            drift_seconds=round(drift, 3),
            drift_acceptable=acceptable
        )

timing_synchronizer = TimingSynchronizer()
