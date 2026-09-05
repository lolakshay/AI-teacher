"""
Avatar Subsystem Models and Configurations (Agent 5 - Avatar + Voice Engine)
"""

from typing import Optional, Literal
from pydantic import BaseModel, Field

AvatarExpressionType = Literal[
    "neutral",
    "friendly",
    "focused",
    "engaged",
    "curious",
    "encouraging",
    "supportive",
    "patient",
    "confident",
    "attentive",
    "thoughtful",
    "celebrating"
]

TeacherGestureType = Literal[
    "none",
    "explain",
    "point_visual",
    "emphasize",
    "welcome",
    "thinking"
]

AvatarPositionType = Literal[
    "left",
    "right",
    "center",
    "pip"
]

class AvatarConfig(BaseModel):
    """
    Configuration parameters for Synthetic Teacher Avatar synthesis.
    Provides styling, positioning, and camera bounds for Agent 4 compositing.
    """
    avatar_id: str = Field(default="teacher_avatar_01", description="Identifier for teacher persona/avatar")
    provider: Optional[str] = Field(default=None, description="Optional override for avatar provider")
    style: str = Field(default="professional_teacher", description="Visual styling theme")
    background: str = Field(default="transparent_or_neutral", description="Background mode (transparent, neutral, classroom)")
    position: AvatarPositionType = Field(default="right", description="Screen docking coordinate for Agent 4 composer")
    scale: float = Field(default=1.0, ge=0.5, le=2.0, description="Scale multiplier for video compositing")
    expression: AvatarExpressionType = Field(default="friendly", description="Facial expression state")
    gesture: Optional[TeacherGestureType] = Field(default=None, description="Teacher hand/body gesture")

class AvatarError(Exception):
    """Custom exception raised by avatar providers and services."""
    def __init__(self, message: str, code: str = "AVATAR_GENERATION_FAILED", retryable: bool = False):
        super().__init__(message)
        self.message = message
        self.code = code
        self.retryable = retryable
