"""
Asset Contracts and Aggregated Results (Agent 5 - Avatar + Voice Engine)
Primary data contract consumed by Agent 4 (AI Teaching Video Engine).
"""

from typing import Optional, Dict, Any, List, Literal
from pydantic import BaseModel, Field
from datetime import datetime, timezone
import uuid
from backend.avatar_voice.models.voice import SpeechSegment

FallbackLevel = Literal["full_presentation", "audio_only", "text_only"]

class NormalizedError(BaseModel):
    """Normalized, user-safe error representation."""
    code: str = Field(description="Machine-readable error code")
    message: str = Field(description="User-friendly error message")
    retryable: bool = Field(default=False, description="Whether client should attempt retry")

class AudioAsset(BaseModel):
    """Generated audio media asset contract."""
    asset_id: str = Field(default_factory=lambda: f"audio_{uuid.uuid4().hex[:10]}")
    audio_url: Optional[str] = None
    local_path: Optional[str] = None
    duration_seconds: float = Field(default=0.0, ge=0.0)
    language: str = "en"
    voice_id: Optional[str] = None
    sample_rate: int = 24000
    format: str = "wav"
    provider: str = "mock"
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    metadata: Dict[str, Any] = Field(default_factory=dict)

class AvatarAsset(BaseModel):
    """Generated avatar video media asset contract."""
    asset_id: str = Field(default_factory=lambda: f"avatar_{uuid.uuid4().hex[:10]}")
    video_url: Optional[str] = None
    local_path: Optional[str] = None
    duration_seconds: float = Field(default=0.0, ge=0.0)
    width: int = 1280
    height: int = 720
    fps: int = 30
    language: str = "en"
    avatar_id: Optional[str] = None
    provider: str = "mock"
    lip_synced: bool = True
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    metadata: Dict[str, Any] = Field(default_factory=dict)

class SceneTiming(BaseModel):
    """Timing metadata synchronizing audio, avatar, and visuals."""
    duration_seconds: float = Field(default=0.0, ge=0.0)
    segments: List[SpeechSegment] = Field(default_factory=list)
    audio_duration: float = Field(default=0.0)
    avatar_duration: float = Field(default=0.0)
    drift_seconds: float = Field(default=0.0)
    drift_acceptable: bool = True

class AudioSummary(BaseModel):
    asset_id: str
    url: Optional[str] = None
    local_path: Optional[str] = None
    duration_seconds: float = 0.0

class AvatarSummary(BaseModel):
    asset_id: str
    url: Optional[str] = None
    local_path: Optional[str] = None
    duration_seconds: float = 0.0
    lip_synced: bool = True

class PresentationMetadata(BaseModel):
    expression: str = "friendly"
    gesture: Optional[str] = None
    position: str = "right"
    scale: float = 1.0

class AvatarVoiceSceneResult(BaseModel):
    """
    Primary integration contract provided by Agent 5 to Agent 4 (Video Engine).
    Conforms strictly to Section 38 of the system architecture.
    """
    scene_id: str = Field(default_factory=lambda: f"scene_{uuid.uuid4().hex[:8]}")
    status: str = Field(default="ready", description="ready, partial, failed, processing")
    spoken_text: str
    display_text: Optional[str] = None
    language: str = "en"
    audio: Optional[AudioSummary] = None
    avatar: Optional[AvatarSummary] = None
    timing: SceneTiming = Field(default_factory=SceneTiming)
    presentation: PresentationMetadata = Field(default_factory=PresentationMetadata)
    fallback: Optional[str] = Field(default=None, description="null, audio_only, text_only")
    error: Optional[NormalizedError] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
