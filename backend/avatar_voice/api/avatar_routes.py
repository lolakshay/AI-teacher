"""
Avatar and Scene API Routes (Agent 5 - Avatar + Voice Engine)
Provides endpoints for avatar synthesis, synchronized scene generation, and binary asset streaming.
"""

from typing import Optional, Dict, Any
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from pathlib import Path

from backend.app.core.config import settings
from backend.avatar_voice.models.avatar import AvatarConfig, AvatarError, AvatarExpressionType
from backend.avatar_voice.models.voice import VoiceConfig
from backend.avatar_voice.models.assets import AudioAsset, AvatarVoiceSceneResult
from backend.avatar_voice.services.avatar_service import avatar_service
from backend.avatar_voice.services.scene_service import scene_service

router = APIRouter(tags=["Avatar & Scene Engine"])

# Store generated scenes in memory for quick retrieval
_scene_store: Dict[str, AvatarVoiceSceneResult] = {}

class AvatarGenerateRequest(BaseModel):
    text: Optional[str] = Field(default="Welcome to your lesson", description="Spoken text to synchronize avatar video against")
    emotion: Optional[str] = Field(default=None, description="Pedagogical emotion keyword e.g. explaining, patient")
    expression: Optional[str] = Field(default=None, description="Teacher expression keyword")
    language: str = Field(default="en")
    audio_asset_id: Optional[str] = None
    avatar_config: Optional[AvatarConfig] = None

class AvatarSceneGenerateRequest(BaseModel):
    spoken_text: str = Field(description="Spoken teaching script or explanation")
    language: str = Field(default="en")
    voice_config: Optional[VoiceConfig] = None
    avatar_config: Optional[AvatarConfig] = None
    expression: Optional[str] = None
    scene_intent: Optional[str] = Field(default=None, description="Pedagogical context e.g. explanation, reteaching, question")
    scene_id: Optional[str] = None

@router.post("/avatar/generate")
def generate_avatar(payload: AvatarGenerateRequest):
    """Generates synthetic avatar video synchronized to audio."""
    try:
        spoken_content = payload.text or "Welcome to your lesson"
        intent = payload.emotion or payload.expression or "friendly"
        audio_asset = AudioAsset(
            asset_id=payload.audio_asset_id or "audio_direct",
            duration_seconds=max(1.5, len(spoken_content.split()) / 2.5),
            language=payload.language
        )
        res = avatar_service.generate_avatar(
            spoken_text=spoken_content,
            audio_asset=audio_asset,
            language=payload.language,
            avatar_config=payload.avatar_config,
            pedagogical_intent=intent
        )
        return {
            "status": "success",
            "avatar_asset": res["avatar_asset"],
            "expression": res["expression"],
            "gesture": res["gesture"],
            "cache_hit": res["cache_hit"]
        }
    except AvatarError as ae:
        raise HTTPException(
            status_code=400 if "AUTH" not in ae.code else 401,
            detail={"code": ae.code, "message": ae.message, "retryable": ae.retryable}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail={"code": "AVATAR_GENERATION_FAILED", "message": str(e)})

@router.get("/avatar/providers")
def list_avatar_providers():
    """Lists supported avatar providers and teacher avatars."""
    return {
        "active_provider": getattr(settings, "AVATAR_PROVIDER", "mock"),
        "supported_avatars": avatar_service.get_supported_avatars()
    }

@router.get("/avatar/{asset_id}")
def get_avatar_asset_info(asset_id: str):
    """Returns metadata for an avatar video asset."""
    file_mp4 = Path(settings.AVATAR_CACHE_DIR) / f"{asset_id}.mp4"
    if not file_mp4.exists():
        raise HTTPException(status_code=404, detail={"code": "ASSET_NOT_FOUND", "message": "Avatar asset not found"})

    return {
        "asset_id": asset_id,
        "format": "mp4",
        "url": f"/api/avatar-voice/assets/video/{asset_id}",
        "local_path": str(file_mp4)
    }

@router.post("/avatar-scene/generate", response_model=AvatarVoiceSceneResult)
def generate_avatar_scene(payload: AvatarSceneGenerateRequest):
    """
    Primary endpoint for Agent 4 and Agent 1.
    Converts spoken teaching text into audio, avatar video, timing, and presentation metadata.
    """
    intent = payload.scene_intent or payload.expression or "explanation"
    result = scene_service.generate_scene(
        spoken_text=payload.spoken_text,
        language=payload.language,
        voice_config=payload.voice_config,
        avatar_config=payload.avatar_config,
        pedagogical_intent=intent,
        scene_id=payload.scene_id
    )
    _scene_store[result.scene_id] = result
    return result

@router.get("/avatar-scene/{scene_id}", response_model=AvatarVoiceSceneResult)
def get_avatar_scene(scene_id: str):
    """Retrieves an already generated scene result by scene_id."""
    if scene_id in _scene_store:
        return _scene_store[scene_id]
    raise HTTPException(status_code=404, detail={"code": "SCENE_NOT_FOUND", "message": "Scene not found"})

# ----------------- BINARY ASSET STREAMING ENDPOINTS -----------------

@router.get("/avatar-voice/assets/audio/{asset_id}")
def stream_audio_asset(asset_id: str):
    """Streams generated audio binary (WAV / MP3)."""
    wav_path = Path(settings.VOICE_CACHE_DIR) / f"{asset_id}.wav"
    mp3_path = Path(settings.VOICE_CACHE_DIR) / f"{asset_id}.mp3"

    if wav_path.exists():
        return FileResponse(str(wav_path), media_type="audio/wav", filename=f"{asset_id}.wav")
    elif mp3_path.exists():
        return FileResponse(str(mp3_path), media_type="audio/mpeg", filename=f"{asset_id}.mp3")
    else:
        raise HTTPException(status_code=404, detail="Audio file not found")

@router.get("/avatar-voice/assets/video/{asset_id}")
def stream_video_asset(asset_id: str):
    """Streams generated avatar video binary (MP4)."""
    mp4_path = Path(settings.AVATAR_CACHE_DIR) / f"{asset_id}.mp4"
    if mp4_path.exists():
        return FileResponse(str(mp4_path), media_type="video/mp4", filename=f"{asset_id}.mp4")
    else:
        raise HTTPException(status_code=404, detail="Avatar video file not found")
