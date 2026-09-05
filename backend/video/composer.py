"""
Video Composer Subsystem (Agent 4)
Orchestrates scene assembly, video encoding (MP4), and multi-asset fallback.
Conforms strictly to Sections 20, 21, 22, 24, 36, 37, 45 of Agent 4 specification.
"""

import os
import uuid
from pathlib import Path
from typing import List, Dict, Any, Optional
import cv2
import numpy as np
from PIL import Image

from backend.video.schemas import (
    VideoScene,
    RenderedVideo,
    VideoStatus
)
from backend.video.visual_renderer import visual_renderer


class VideoComposer:
    """
    Composes individual VideoScenes into a unified 1080p MP4 educational video.
    Synchronizes audio and visual durations, and falls back gracefully to
    synchronized scene assets if video encoding is unavailable.
    """
    def __init__(self, output_dir: Optional[Path] = None):
        if output_dir is None:
            from backend.app.core.config import settings
            self.output_dir = settings.UPLOAD_DIR / "video_assets" / "output"
        else:
            self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def compose_video(
        self,
        video_id: str,
        scenes: List[VideoScene],
        resolution: str = "1920x1080",
        fps: int = 2
    ) -> RenderedVideo:
        """
        Compiles list of VideoScenes into an educational video.
        Ensures all visual frames exist, synchronizes audio/visual timing,
        and outputs MP4 video or structured fallback.
        """
        if not scenes:
            return RenderedVideo(
                video_id=video_id,
                status=VideoStatus.FAILED,
                error="No scenes provided for video composition",
                progress=0
            )

        width, height = (1920, 1080) if resolution == "1920x1080" else (1280, 720)
        total_duration = 0.0
        frame_paths: List[tuple[str, float]] = []

        # 1. Render and synchronize all scene frames
        for scene in scenes:
            # Sync timing: audio duration takes precedence (Section 24 & 36)
            if scene.audio and scene.audio.duration_seconds > 0:
                scene.duration_seconds = scene.audio.duration_seconds
            total_duration += scene.duration_seconds

            # Render deterministic visual frame if not already cached/rendered
            frame_path = None
            if scene.frame_url and os.path.exists(scene.frame_url):
                frame_path = scene.frame_url
            else:
                try:
                    frame_path = visual_renderer.render_scene_visual(scene.scene_id, scene.visual)
                    scene.frame_url = f"/static/videos/frames/{Path(frame_path).name}"
                except Exception as e:
                    # Fallback visual frame
                    fallback_spec = {"title": "Educational Instruction", "definition": scene.spoken_text}
                    frame_path = visual_renderer.render_scene_visual(scene.scene_id, fallback_spec)
                    scene.frame_url = f"/static/videos/frames/{Path(frame_path).name}"

            frame_paths.append((frame_path, scene.duration_seconds))

        mp4_filename = f"{video_id}.mp4"
        out_mp4_path = self.output_dir / mp4_filename
        file_url = f"/static/videos/output/{mp4_filename}"

        # 2. Attempt native MP4 encoding using OpenCV
        encoding_succeeded = False
        try:
            fourcc = cv2.VideoWriter_fourcc(*"mp4v")
            writer = cv2.VideoWriter(str(out_mp4_path), fourcc, fps, (width, height))

            if writer.isOpened():
                for f_path, duration in frame_paths:
                    if not f_path or not os.path.exists(f_path):
                        continue
                    # Load frame image
                    img = Image.open(f_path).convert("RGB")
                    if img.size != (width, height):
                        img = img.resize((width, height), Image.Resampling.LANCZOS)
                    frame_np = np.array(img)
                    # Convert RGB to BGR for OpenCV
                    frame_bgr = cv2.cvtColor(frame_np, cv2.COLOR_RGB2BGR)

                    # Number of video frames for this scene duration
                    num_frames = max(1, int(round(duration * fps)))
                    for _ in range(num_frames):
                        writer.write(frame_bgr)

                writer.release()
                encoding_succeeded = out_mp4_path.exists() and (out_mp4_path.stat().st_size > 1000)
        except Exception as e:
            encoding_succeeded = False

        # 3. Handle Fallback Strategy (Section 21)
        # If full video rendering is constrained, return scene sequence and assets so frontend plays them
        first_frame = frame_paths[0][0] if frame_paths else None
        thumb_url = f"/static/videos/frames/{Path(first_frame).name}" if first_frame else None

        if encoding_succeeded:
            return RenderedVideo(
                video_id=video_id,
                status=VideoStatus.READY,
                file_url=file_url,
                duration_seconds=round(total_duration, 1),
                resolution=resolution,
                format="mp4",
                scenes=scenes,
                thumbnail_url=thumb_url,
                progress=100
            )
        else:
            # Multi-asset video playback fallback
            return RenderedVideo(
                video_id=video_id,
                status=VideoStatus.PARTIAL,
                file_url=None,  # Frontend will play synchronized scenes
                duration_seconds=round(total_duration, 1),
                resolution=resolution,
                format="scenes_bundle",
                scenes=scenes,
                thumbnail_url=thumb_url,
                progress=100
            )


video_composer = VideoComposer()
