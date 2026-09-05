"""
Video Engine Service (Agent 4)
Provides core business logic for interactive step rendering, batch lesson compilation,
video lifecycle tracking, and caching.
Conforms strictly to Sections 1, 23, 38, 39, 40, 41, 46, 51.
"""

import uuid
import os
from typing import List, Dict, Any, Optional, Union
from datetime import datetime, timezone

from backend.video.schemas import (
    VideoLesson,
    VideoScene,
    VideoStatus,
    RenderedVideo
)
from backend.video.scene_planner import VideoScenePlanner
from backend.video.composer import video_composer
from backend.video.cache import asset_cache
from backend.video.providers.voice_provider import VoiceProvider, MockVoiceProvider
from backend.video.providers.avatar_provider import AvatarProvider, MockAvatarProvider


class VideoEngineService:
    """
    Central service interface for the AI Teaching Video Engine.
    Exposes interactive single-step generation and batch lesson composition.
    """
    def __init__(
        self,
        scene_planner: Optional[VideoScenePlanner] = None,
        voice_provider: Optional[VoiceProvider] = None,
        avatar_provider: Optional[AvatarProvider] = None
    ):
        self.voice_provider = voice_provider or MockVoiceProvider()
        self.avatar_provider = avatar_provider or MockAvatarProvider()
        self.scene_planner = scene_planner or VideoScenePlanner(
            voice_provider=self.voice_provider,
            avatar_provider=self.avatar_provider
        )
        
        # In-memory registry for video sessions and lessons
        self._lessons: Dict[str, VideoLesson] = {}
        self._rendered_videos: Dict[str, RenderedVideo] = {}

    def render_teaching_step(
        self,
        step: Any,
        mode: str = "interactive"
    ) -> List[VideoScene]:
        """
        Interactive Mode (Section 39 & 53):
        Consumes single TeachingStep and produces synchronized VideoScene objects.
        Renders visual frames and checks asset cache.
        """
        scenes = self.scene_planner.plan_scenes_for_step(step)

        # Pre-render visual frames for each scene in this step
        for sc in scenes:
            cache_key = asset_cache.generate_cache_key(
                sc.spoken_text,
                sc.audio.language if sc.audio else "Hinglish",
                sc.visual,
                sc.avatar.expression if sc.avatar else "explaining"
            )
            cached = asset_cache.get_cached_asset(cache_key)
            if cached and "frame_url" in cached:
                sc.frame_url = cached["frame_url"]
            else:
                try:
                    from backend.video.visual_renderer import visual_renderer
                    frame_path = visual_renderer.render_scene_visual(sc.scene_id, sc.visual)
                    frame_url = f"/static/videos/frames/{os.path.basename(frame_path)}"
                    sc.frame_url = frame_url
                    asset_cache.store_cached_asset(cache_key, {"frame_url": frame_url, "duration": sc.duration_seconds})
                except Exception as e:
                    sc.frame_url = None

        return scenes

    def generate_lesson_video(
        self,
        session_id: str,
        lesson_id: str,
        teaching_steps: List[Any],
        title: str = "Educational Lesson",
        language: str = "Hinglish",
        mode: str = "batch"
    ) -> VideoLesson:
        """
        Batch Mode (Section 40 & 41):
        Compiles a list of TeachingSteps into a unified VideoLesson and renders video.
        """
        video_id = f"video_{uuid.uuid4().hex[:8]}"
        all_scenes: List[VideoScene] = []

        # 1. Status: PLANNING
        lesson = VideoLesson(
            video_lesson_id=video_id,
            session_id=session_id,
            lesson_id=lesson_id,
            title=title,
            language=language,
            status=VideoStatus.PLANNING,
            progress=15,
            scenes=[]
        )
        self._lessons[video_id] = lesson

        # 2. Plan all scenes across teaching steps
        for step in teaching_steps:
            step_scenes = self.render_teaching_step(step, mode=mode)
            all_scenes.extend(step_scenes)

        # Re-index scenes sequentially
        for idx, sc in enumerate(all_scenes):
            sc.scene_index = idx

        lesson.scenes = all_scenes
        lesson.progress = 50
        lesson.status = VideoStatus.COMPOSING

        # 3. Video Composition (Section 20)
        rendered = video_composer.compose_video(video_id=video_id, scenes=all_scenes)
        self._rendered_videos[video_id] = rendered

        # 4. Final status update
        lesson.status = rendered.status
        lesson.progress = rendered.progress
        lesson.video_url = rendered.file_url
        lesson.thumbnail_url = rendered.thumbnail_url
        lesson.duration_seconds = rendered.duration_seconds

        self._lessons[video_id] = lesson
        return lesson

    def get_video_lesson(self, video_id: str) -> Optional[VideoLesson]:
        """Returns VideoLesson metadata and current status."""
        return self._lessons.get(video_id)

    def get_video_scenes(self, video_id: str) -> Optional[List[VideoScene]]:
        """Returns scene metadata sequence for a video."""
        lesson = self._lessons.get(video_id)
        if lesson:
            return lesson.scenes
        rendered = self._rendered_videos.get(video_id)
        if rendered:
            return rendered.scenes
        return None

    def render_single_scene_debug(self, scene_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Development / Debug endpoint to test raw visual rendering."""
        from backend.video.visual_renderer import visual_renderer
        scene_id = scene_dict.get("scene_id", f"debug_{uuid.uuid4().hex[:6]}")
        visual_spec = scene_dict.get("visual", {})
        frame_path = visual_renderer.render_scene_visual(scene_id, visual_spec)
        return {
            "scene_id": scene_id,
            "frame_path": frame_path,
            "frame_url": f"/static/videos/frames/{os.path.basename(frame_path)}"
        }


video_service = VideoEngineService()
