"""
Scene Generation Service (Agent 5 - Avatar + Voice Engine)
End-to-end presentation orchestrator connecting voice synthesis, avatar video generation,
timing synchronization, and multi-tiered fallback handling.
Provides the primary data contract consumed by Agent 4 (AI Teaching Video Engine).
"""

from typing import Dict, Any, Optional
import uuid

from backend.avatar_voice.models.assets import (
    AvatarVoiceSceneResult, AudioAsset, AvatarAsset,
    AudioSummary, AvatarSummary, PresentationMetadata,
    NormalizedError
)
from backend.avatar_voice.models.voice import VoiceConfig, VoiceError
from backend.avatar_voice.models.avatar import AvatarConfig, AvatarError
from backend.avatar_voice.services.voice_service import voice_service
from backend.avatar_voice.services.avatar_service import avatar_service
from backend.avatar_voice.processing.timing import timing_synchronizer

class SceneService:
    """
    Coordinates synchronized scene rendering for teaching steps.
    """

    def generate_scene(
        self,
        spoken_text: str,
        language: str = "en",
        voice_config: Optional[VoiceConfig] = None,
        avatar_config: Optional[AvatarConfig] = None,
        pedagogical_intent: Optional[str] = None,
        scene_id: Optional[str] = None
    ) -> AvatarVoiceSceneResult:
        """
        Executes complete scene pipeline:
        Voice generation -> Avatar generation -> Timing synchronization -> Agent 4 Data Contract.
        Implements graceful fallbacks (Level 1: Full -> Level 3: Audio Only -> Level 4: Text Only).
        """
        sid = scene_id or f"scene_{uuid.uuid4().hex[:8]}"
        v_config = voice_config or VoiceConfig(language=language)
        a_config = avatar_config or AvatarConfig()

        audio_res = None
        avatar_res = None
        error_info = None
        status = "ready"
        fallback_mode = None

        # 1. Voice Synthesis Pipeline
        try:
            audio_res = voice_service.synthesize(
                raw_text=spoken_text,
                language=language,
                voice_config=v_config
            )
        except VoiceError as ve:
            error_info = NormalizedError(code=ve.code, message=ve.message, retryable=ve.retryable)
            return AvatarVoiceSceneResult(
                scene_id=sid,
                status="failed",
                spoken_text=spoken_text,
                language=language,
                fallback="text_only",
                error=error_info,
                presentation=PresentationMetadata(expression="neutral")
            )
        except Exception as e:
            error_info = NormalizedError(
                code="VOICE_GENERATION_FAILED",
                message=f"Voice synthesis failed: {str(e)}",
                retryable=True
            )
            return AvatarVoiceSceneResult(
                scene_id=sid,
                status="failed",
                spoken_text=spoken_text,
                language=language,
                fallback="text_only",
                error=error_info,
                presentation=PresentationMetadata(expression="neutral")
            )

        audio_asset: AudioAsset = audio_res["audio_asset"]
        segments = audio_res["segments"]
        display_text = audio_res["display_text"]

        # 2. Avatar Synthesis Pipeline
        try:
            avatar_res = avatar_service.generate_avatar(
                spoken_text=spoken_text,
                audio_asset=audio_asset,
                language=language,
                avatar_config=a_config,
                pedagogical_intent=pedagogical_intent,
                duration=audio_asset.duration_seconds
            )
        except (AvatarError, Exception) as ae:
            # LEVEL 3 FALLBACK: Voice succeeds, Avatar fails -> Return audio_only
            status = "partial"
            fallback_mode = "audio_only"
            err_msg = getattr(ae, "message", str(ae))
            err_code = getattr(ae, "code", "AVATAR_GENERATION_FAILED")
            error_info = NormalizedError(code=err_code, message=err_msg, retryable=getattr(ae, "retryable", True))

        # 3. Timing Calibration
        avatar_asset: Optional[AvatarAsset] = avatar_res["avatar_asset"] if avatar_res else None
        avatar_duration = avatar_asset.duration_seconds if avatar_asset else audio_asset.duration_seconds

        timing = timing_synchronizer.synchronize(
            audio_duration=audio_asset.duration_seconds,
            avatar_duration=avatar_duration,
            segments=segments
        )

        # 4. Presentation Metadata
        resolved_expr = avatar_res["expression"] if avatar_res else a_config.expression
        resolved_gesture = avatar_res["gesture"] if avatar_res else a_config.gesture

        presentation = PresentationMetadata(
            expression=resolved_expr,
            gesture=resolved_gesture,
            position=a_config.position,
            scale=a_config.scale
        )

        # 5. Build Summaries
        audio_summary = AudioSummary(
            asset_id=audio_asset.asset_id,
            url=audio_asset.audio_url,
            local_path=audio_asset.local_path,
            duration_seconds=audio_asset.duration_seconds
        )

        avatar_summary = None
        if avatar_asset:
            avatar_summary = AvatarSummary(
                asset_id=avatar_asset.asset_id,
                url=avatar_asset.video_url,
                local_path=avatar_asset.local_path,
                duration_seconds=avatar_asset.duration_seconds,
                lip_synced=avatar_asset.lip_synced
            )

        return AvatarVoiceSceneResult(
            scene_id=sid,
            status=status,
            spoken_text=audio_res["spoken_text"],
            display_text=display_text,
            language=language,
            audio=audio_summary,
            avatar=avatar_summary,
            timing=timing,
            presentation=presentation,
            fallback=fallback_mode,
            error=error_info,
            metadata={
                "voice_cache_hit": audio_res.get("cache_hit", False),
                "avatar_cache_hit": avatar_res.get("cache_hit", False) if avatar_res else False,
                "pedagogical_intent": pedagogical_intent
            }
        )

    def generate_scene_for_teaching_step(
        self,
        step: Any,
        voice_config: Optional[VoiceConfig] = None,
        avatar_config: Optional[AvatarConfig] = None
    ) -> AvatarVoiceSceneResult:
        """
        Primary adapter method for Agent 4 and Agent 1.
        Accepts any TeachingStep instance and translates pedagogical context into a renderable scene.
        """
        # Extract speech text: prefer spoken_script, fallback to explanation or content
        spoken_text = getattr(step, "spoken_script", None)
        if not spoken_text:
            spoken_text = getattr(step, "explanation", None) or getattr(step, "content", "")

        language = getattr(step, "language", "en")
        
        # Determine intent
        step_type = getattr(step, "step_type", "explanation")
        avatar_emotion = getattr(step, "avatar_emotion", None)
        intent = avatar_emotion or step_type

        # Question scene detection
        has_question = getattr(step, "question", None) is not None or step_type == "question"
        if has_question and intent not in ["encouraging", "celebrating"]:
            intent = "question"
        elif step_type in ["re_explanation", "reteaching"]:
            intent = "re_explanation"

        step_id = getattr(step, "step_id", None)

        return self.generate_scene(
            spoken_text=spoken_text,
            language=language,
            voice_config=voice_config,
            avatar_config=avatar_config,
            pedagogical_intent=intent,
            scene_id=f"scene_{step_id}" if step_id else None
        )

scene_service = SceneService()
