"""
Voice API Routes (Agent 5 - Avatar + Voice Engine)
"""

from typing import Optional, Dict, Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from pathlib import Path

from backend.app.core.config import settings
from backend.avatar_voice.models.voice import VoiceConfig, VoiceError
from backend.avatar_voice.services.voice_service import voice_service

router = APIRouter(prefix="/voice", tags=["Voice Engine"])

class VoiceGenerateRequest(BaseModel):
    text: str = Field(description="Spoken text or educational script to synthesize")
    language: str = Field(default="en", description="Spoken language code (e.g. en, hi, hinglish)")
    voice_config: Optional[VoiceConfig] = None

@router.post("/generate")
def generate_voice(payload: VoiceGenerateRequest):
    """Generates TTS audio asset and timing segments from input text."""
    try:
        result = voice_service.synthesize(
            raw_text=payload.text,
            language=payload.language,
            voice_config=payload.voice_config
        )
        return {
            "status": "success",
            "audio_asset": result["audio_asset"],
            "segments": result["segments"],
            "display_text": result["display_text"],
            "spoken_text": result["spoken_text"],
            "cache_hit": result["cache_hit"]
        }
    except VoiceError as ve:
        raise HTTPException(
            status_code=400 if "AUTH" not in ve.code else 401,
            detail={"code": ve.code, "message": ve.message, "retryable": ve.retryable}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail={"code": "VOICE_GENERATION_FAILED", "message": str(e)})

@router.get("/providers")
def list_providers():
    """Lists supported voice providers and voices."""
    return {
        "active_provider": getattr(settings, "VOICE_PROVIDER", "mock"),
        "supported_voices": voice_service.get_supported_voices("en")
    }

@router.get("/{asset_id}")
def get_voice_asset_info(asset_id: str):
    """Returns metadata for a generated voice asset."""
    file_wav = Path(settings.VOICE_CACHE_DIR) / f"{asset_id}.wav"
    file_mp3 = Path(settings.VOICE_CACHE_DIR) / f"{asset_id}.mp3"
    target_path = file_wav if file_wav.exists() else (file_mp3 if file_mp3.exists() else None)
    
    if not target_path:
        raise HTTPException(status_code=404, detail={"code": "ASSET_NOT_FOUND", "message": "Voice asset not found"})

    return {
        "asset_id": asset_id,
        "format": target_path.suffix.replace(".", ""),
        "url": f"/api/avatar-voice/assets/audio/{asset_id}",
        "local_path": str(target_path)
    }
