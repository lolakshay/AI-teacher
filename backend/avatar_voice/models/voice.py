"""
Voice Subsystem Models and Configurations (Agent 5 - Avatar + Voice Engine)
"""

from typing import Optional, Literal
from pydantic import BaseModel, Field
import uuid

VoiceStyleType = Literal[
    "friendly",
    "professional",
    "energetic",
    "calm",
    "encouraging",
    "serious",
    "conversational",
    "patient",
    "curious"
]

class VoiceConfig(BaseModel):
    """
    Configuration parameters for Text-to-Speech synthesis.
    Safe against unsupported provider parameters.
    """
    voice_id: Optional[str] = Field(default=None, description="Provider-specific voice identifier")
    language: str = Field(default="en", description="Target spoken language code (e.g. en, hi, hinglish)")
    speaking_rate: float = Field(default=1.0, ge=0.5, le=2.0, description="Relative speech speed multiplier")
    pitch: float = Field(default=0.0, ge=-20.0, le=20.0, description="Pitch adjustment in semitones or percentage")
    volume: float = Field(default=1.0, ge=0.0, le=1.0, description="Audio volume multiplier")
    style: VoiceStyleType = Field(default="friendly", description="Pedagogical vocal tone/style")
    gender: Optional[str] = Field(default=None, description="Optional gender preference (male, female, neutral)")
    provider: Optional[str] = Field(default=None, description="Optional override for voice provider")

class SpeechSegment(BaseModel):
    """
    Structured temporal unit of speech used by Agent 4 to align visual graphics/equations.
    """
    segment_id: str = Field(default_factory=lambda: f"seg_{uuid.uuid4().hex[:8]}")
    text: str = Field(description="Spoken text in this segment")
    display_text: Optional[str] = Field(default=None, description="Corresponding visual display text (if LaTeX/math)")
    start_seconds: float = Field(default=0.0, ge=0.0)
    end_seconds: float = Field(default=0.0, ge=0.0)
    emphasis: bool = Field(default=False, description="Whether this segment conveys key educational emphasis")

class VoiceError(Exception):
    """Custom exception raised by voice providers and services."""
    def __init__(self, message: str, code: str = "VOICE_GENERATION_FAILED", retryable: bool = False):
        super().__init__(message)
        self.message = message
        self.code = code
        self.retryable = retryable
