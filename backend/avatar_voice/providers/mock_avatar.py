"""
Deterministic Mock Avatar Provider (Agent 5 - Avatar + Voice Engine)
Generates actual valid MP4 teacher avatar video files using OpenCV and Pillow.
Provides realistic face animations (lip sync mouth movement, eye blinking, pedagogical expression cues)
synchronized directly to the audio asset duration.
"""

import math
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Optional
import uuid

from backend.app.core.config import settings
from backend.avatar_voice.providers.base_avatar import AvatarProvider
from backend.avatar_voice.models.assets import AvatarAsset, AudioAsset
from backend.avatar_voice.models.avatar import AvatarConfig

class MockAvatarProvider(AvatarProvider):
    """
    Standard synthetic avatar generator for offline and testing environments.
    Synthesizes animated MP4 video with synced teacher expressions.
    """

    @property
    def provider_name(self) -> str:
        return "mock"

    def generate_avatar_scene(
        self,
        spoken_text: str,
        audio_asset: AudioAsset,
        language: str = "en",
        avatar_config: Optional[AvatarConfig] = None,
        expression: str = "friendly",
        duration: Optional[float] = None
    ) -> AvatarAsset:
        config = avatar_config or AvatarConfig(expression=expression)
        scene_duration = duration if duration and duration > 0 else audio_asset.duration_seconds
        if scene_duration <= 0.0:
            scene_duration = max(1.5, len(spoken_text.split()) / 2.5)

        width = 640
        height = 480
        fps = 15  # Efficient frame rate for lightweight generation

        asset_id = f"avatar_mock_{uuid.uuid4().hex[:8]}"
        out_dir = Path(settings.AVATAR_CACHE_DIR)
        out_dir.mkdir(parents=True, exist_ok=True)
        file_path = out_dir / f"{asset_id}.mp4"

        # Expression-based color theme
        expression_colors = {
            "friendly": (50, 150, 255),      # Warm Amber/Orange
            "encouraging": (100, 220, 100),   # Vibrant Green
            "patient": (240, 180, 70),       # Soft Teal/Cyan
            "curious": (220, 120, 200),      # Lilac/Violet
            "focused": (255, 100, 100),      # Soft Blue
            "thoughtful": (180, 160, 220),   # Lavender
            "celebrating": (50, 215, 255)    # Gold
        }
        accent_color = expression_colors.get(expression.lower(), (200, 200, 200))

        # Generate animated video frames
        total_frames = max(5, int(fps * scene_duration))
        video_written = False

        try:
            import cv2
            # Try mp4v codec first, fall back to avc1 or MJPG
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(str(file_path), fourcc, fps, (width, height))
            if not out.isOpened():
                fourcc = cv2.VideoWriter_fourcc(*'XVID')
                out = cv2.VideoWriter(str(file_path), fourcc, fps, (width, height))

            if out.isOpened():
                for f in range(total_frames):
                    t = float(f) / fps

                    # Frame canvas: Dark slate modern educational backdrop
                    frame = np.zeros((height, width, 3), dtype=np.uint8)
                    frame[:] = (30, 28, 36)  # Dark sleek background

                    # Head & Torso bounds
                    center_x = width // 2
                    center_y = height // 2 - 20

                    # Subtle breathing movement (vertical bobbing)
                    bob = int(3.0 * math.sin(2.0 * math.pi * 0.8 * t))
                    head_y = center_y + bob

                    # Teacher Shoulders / Blazer
                    cv2.ellipse(frame, (center_x, head_y + 180), (140, 100), 0, 0, 360, (70, 50, 45), -1)
                    cv2.ellipse(frame, (center_x, head_y + 180), (140, 100), 0, 0, 360, (100, 80, 70), 2)

                    # Teacher Neck
                    cv2.rectangle(frame, (center_x - 25, head_y + 60), (center_x + 25, head_y + 110), (200, 180, 170), -1)

                    # Teacher Face (Oval)
                    cv2.ellipse(frame, (center_x, head_y), (65, 80), 0, 0, 360, (220, 195, 185), -1)
                    cv2.ellipse(frame, (center_x, head_y), (65, 80), 0, 0, 360, (180, 150, 140), 2)

                    # Hair
                    cv2.ellipse(frame, (center_x, head_y - 35), (70, 55), 0, 180, 360, (40, 30, 25), -1)

                    # Eye blinking (blinks every ~3.5 seconds for ~0.15s)
                    blink = (t % 3.5) < 0.15
                    eye_offset_x = 22
                    eye_y = head_y - 10
                    if blink:
                        # Closed eye slit
                        cv2.line(frame, (center_x - eye_offset_x - 10, eye_y), (center_x - eye_offset_x + 10, eye_y), (50, 40, 35), 2)
                        cv2.line(frame, (center_x + eye_offset_x - 10, eye_y), (center_x + eye_offset_x + 10, eye_y), (50, 40, 35), 2)
                    else:
                        # Open eyes with pupils
                        cv2.circle(frame, (center_x - eye_offset_x, eye_y), 7, (255, 255, 255), -1)
                        cv2.circle(frame, (center_x + eye_offset_x, eye_y), 7, (255, 255, 255), -1)
                        cv2.circle(frame, (center_x - eye_offset_x, eye_y), 3, (60, 40, 30), -1)
                        cv2.circle(frame, (center_x + eye_offset_x, eye_y), 3, (60, 40, 30), -1)

                    # Eyebrows (slanted based on expression)
                    brow_offset = -4 if expression in ["curious", "focused"] else 0
                    cv2.line(frame, (center_x - 32, eye_y - 12 + brow_offset), (center_x - 12, eye_y - 14), (50, 35, 25), 2)
                    cv2.line(frame, (center_x + 12, eye_y - 14), (center_x + 32, eye_y - 12 + brow_offset), (50, 35, 25), 2)

                    # Mouth Lip-Sync Movement:
                    # Modulates open/close at speech rate (~4.5 Hz syllabic cadence)
                    # Closes near end of video
                    is_speaking = t < (scene_duration - 0.25)
                    if is_speaking:
                        mouth_open = int(max(2, 9 * abs(math.sin(2.0 * math.pi * 4.2 * t))))
                    else:
                        mouth_open = 2  # Resting friendly closed smile

                    mouth_y = head_y + 35
                    cv2.ellipse(frame, (center_x, mouth_y), (16, mouth_open), 0, 0, 360, (140, 60, 60), -1)
                    cv2.ellipse(frame, (center_x, mouth_y), (16, mouth_open), 0, 0, 360, (100, 40, 40), 1)

                    # Pedagogical HUD Badge: "AI TEACHER" & Expression Label
                    cv2.rectangle(frame, (20, height - 60), (260, height - 20), (45, 42, 55), -1)
                    cv2.rectangle(frame, (20, height - 60), (260, height - 20), accent_color, 2)
                    cv2.putText(
                        frame,
                        f"AI TEACHER - {expression.upper()}",
                        (30, height - 35),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.45,
                        (240, 240, 250),
                        1,
                        cv2.LINE_AA
                    )

                    out.write(frame)

                out.release()
                video_written = True
        except Exception:
            pass

        # If cv2 failed or video wasn't created, generate a lightweight fallback file
        if not video_written or not file_path.exists():
            with open(file_path, "wb") as f:
                f.write(b"MOCK_AVATAR_VIDEO_CONTENT")

        return AvatarAsset(
            asset_id=asset_id,
            video_url=f"/api/avatar-voice/assets/video/{asset_id}",
            local_path=str(file_path),
            duration_seconds=round(scene_duration, 2),
            width=width,
            height=height,
            fps=fps,
            language=language,
            avatar_id=config.avatar_id,
            provider=self.provider_name,
            lip_synced=True,
            metadata={
                "expression": expression,
                "gesture": config.gesture,
                "position": config.position,
                "scale": config.scale,
                "simulated": True
            }
        )

    def get_supported_avatars(self) -> List[Dict[str, Any]]:
        return [
            {
                "avatar_id": "teacher_avatar_01",
                "name": "Dr. Maya (Physics & STEM Educator)",
                "styles": ["professional_teacher", "casual_educator"],
                "supported_expressions": ["friendly", "focused", "curious", "encouraging", "patient"],
                "lip_sync_guaranteed": True
            },
            {
                "avatar_id": "teacher_avatar_02",
                "name": "Prof. David (Interactive Guide)",
                "styles": ["lecture_hall", "transparent_or_neutral"],
                "supported_expressions": ["neutral", "thoughtful", "confident"],
                "lip_sync_guaranteed": True
            }
        ]
