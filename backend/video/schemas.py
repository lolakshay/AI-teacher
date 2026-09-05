"""
AI Teaching Video Engine — Core Schemas & Data Contracts
Conforms strictly to Sections 5, 6, 11, 12, 13, 14, 15, 16, 17, 20, 22 of Agent 4 specification.
"""

from typing import List, Dict, Any, Optional, Literal, Union
from pydantic import BaseModel, Field, ConfigDict
from enum import Enum
from datetime import datetime, timezone
import uuid


class VideoStatus(str, Enum):
    QUEUED = "queued"
    PLANNING = "planning"
    GENERATING_AUDIO = "generating_audio"
    GENERATING_AVATAR = "generating_avatar"
    GENERATING_VISUALS = "generating_visuals"
    COMPOSING = "composing"
    READY = "ready"
    FAILED = "failed"
    PARTIAL = "partial"


SceneType = Literal[
    "avatar_explanation",
    "concept_card",
    "diagram",
    "equation",
    "graph",
    "code",
    "timeline",
    "map",
    "process",
    "image",
    "worked_example",
    "question",
    "summary"
]


# ============================================================
# VISUAL SPECIFICATIONS (Section 11 - 17)
# ============================================================

class DiagramElement(BaseModel):
    id: str
    type: str  # component, arrow, block, label, node, wire
    label: str
    properties: Dict[str, Any] = Field(default_factory=dict)


class DiagramRelationship(BaseModel):
    from_id: str = Field(alias="from")
    to_id: str = Field(alias="to")
    relation: str = "connected"  # connected, flows_to, causes, surrounds
    label: Optional[str] = None

    model_config = ConfigDict(populate_by_name=True)


class VisualSpec(BaseModel):
    """Base and generic Visual Specification."""
    type: str = "concept_card"
    title: str = ""
    description: str = ""
    elements: List[Dict[str, Any]] = Field(default_factory=list)
    relationships: List[Dict[str, Any]] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class EquationVisualSpec(BaseModel):
    type: Literal["equation"] = "equation"
    title: str = "Governing Equation"
    equation: str  # LaTeX or mathematical formula (e.g. "V = I * R")
    explanation: List[str] = Field(default_factory=list)  # e.g. ["V = voltage", "I = current", "R = resistance"]
    highlight: Optional[str] = None  # e.g. "R"
    steps: Optional[List[Dict[str, str]]] = None  # Step-by-step algebraic manipulation


class GraphAxis(BaseModel):
    label: str
    unit: Optional[str] = None
    min_val: Optional[float] = 0.0
    max_val: Optional[float] = None


class GraphVisualSpec(BaseModel):
    type: Literal["graph"] = "graph"
    title: str = "Graphical Relationship"
    x_axis: GraphAxis = Field(default_factory=lambda: GraphAxis(label="X"))
    y_axis: GraphAxis = Field(default_factory=lambda: GraphAxis(label="Y"))
    relationship: str = "linear"  # "linear", "inverse", "exponential", "direct"
    data_points: Optional[List[Dict[str, float]]] = None
    annotation: Optional[str] = None


class CodeVisualSpec(BaseModel):
    type: Literal["code"] = "code"
    title: str = "Code Demonstration"
    language: str = "python"
    code: str
    highlight_lines: List[int] = Field(default_factory=list)
    output: Optional[str] = None
    execution_steps: List[str] = Field(default_factory=list)


class TimelineEvent(BaseModel):
    year: str
    title: str
    description: str = ""


class TimelineVisualSpec(BaseModel):
    type: Literal["timeline"] = "timeline"
    title: str = "Historical Timeline"
    events: List[TimelineEvent] = Field(default_factory=list)


class MapVisualSpec(BaseModel):
    type: Literal["map"] = "map"
    title: str = "Geographic & Historical Map"
    region: str = "Global"
    markers: List[Dict[str, Any]] = Field(default_factory=list)
    paths: List[Dict[str, Any]] = Field(default_factory=list)
    labels: List[str] = Field(default_factory=list)
    fallback_instruction: str = "Render geographical context diagram"


class ProcessVisualSpec(BaseModel):
    type: Literal["process"] = "process"
    title: str = "Process Flow"
    current_stage: int = 1
    stages: List[Dict[str, Any]] = Field(default_factory=list)


class ImageVisualSpec(BaseModel):
    type: Literal["image"] = "image"
    title: str = "Educational Image"
    query: str
    purpose: str = "illustrate concept"
    caption: str = ""
    source: str = "educational_archive"
    image_url: Optional[str] = None
    generated: bool = False


class WorkedExampleVisualSpec(BaseModel):
    type: Literal["worked_example"] = "worked_example"
    title: str = "Step-by-Step Worked Example"
    problem: str
    givens: Dict[str, Any] = Field(default_factory=dict)
    formula: str = ""
    steps: List[str] = Field(default_factory=list)
    result: str = ""


class ConceptCardVisualSpec(BaseModel):
    type: Literal["concept_card"] = "concept_card"
    title: str
    subtitle: Optional[str] = None
    definition: str = ""
    key_points: List[str] = Field(default_factory=list)
    badge: Optional[str] = None


# ============================================================
# AVATAR & AUDIO ASSET SPECIFICATIONS (Sections 18, 19)
# ============================================================

class AvatarSceneConfig(BaseModel):
    visible: bool = True
    expression: str = "explaining"  # explaining, thoughtful, attentive, encouraging, celebrating
    position: str = "right"  # "right", "left", "bottom_right", "small", "hidden"
    scale: float = 1.0
    asset_url: Optional[str] = None
    duration_seconds: Optional[float] = None


class AudioSceneConfig(BaseModel):
    audio_url: Optional[str] = None
    duration_seconds: float = 0.0
    language: str = "Hinglish"
    voice_name: Optional[str] = None
    sample_rate: int = 24000


class TransitionConfig(BaseModel):
    type: str = "fade"  # fade, cut, slide_left, dissolve
    duration_seconds: float = 0.5


# ============================================================
# VIDEO SCENE & LESSON (Sections 5, 6)
# ============================================================

class VideoScene(BaseModel):
    scene_id: str = Field(default_factory=lambda: f"scene_{uuid.uuid4().hex[:8]}")
    step_id: str
    scene_index: int = 0
    scene_type: SceneType = "avatar_explanation"
    duration_seconds: float = 15.0
    spoken_text: str = ""
    on_screen_text: List[str] = Field(default_factory=list)
    
    # Visual, Avatar, Audio, Transition payloads
    visual: Dict[str, Any] = Field(default_factory=dict)
    avatar: AvatarSceneConfig = Field(default_factory=AvatarSceneConfig)
    audio: AudioSceneConfig = Field(default_factory=AudioSceneConfig)
    transition: TransitionConfig = Field(default_factory=TransitionConfig)
    
    # Source provenance from uploaded documents / textbooks
    source_references: List[Any] = Field(default_factory=list)
    
    # Interactive question hook for formative assessment pausing
    interactive: bool = False
    pause_video: bool = False
    question_id: Optional[str] = None
    question_text: Optional[str] = None
    options: Optional[List[str]] = None
    hints: List[str] = Field(default_factory=list)
    
    # Rendered frame or asset URL for this specific scene
    frame_url: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class VideoLesson(BaseModel):
    video_lesson_id: str = Field(default_factory=lambda: f"video_{uuid.uuid4().hex[:8]}")
    session_id: str
    lesson_id: str
    title: str
    language: str = "Hinglish"
    duration_seconds: float = 0.0
    status: VideoStatus = VideoStatus.QUEUED
    progress: int = 0  # 0 to 100
    scenes: List[VideoScene] = Field(default_factory=list)
    video_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    resolution: str = "1920x1080"
    format: str = "mp4"
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class RenderedVideo(BaseModel):
    video_id: str
    status: VideoStatus = VideoStatus.READY
    file_url: Optional[str] = None
    duration_seconds: float = 0.0
    resolution: str = "1920x1080"
    format: str = "mp4"
    scenes: List[VideoScene] = Field(default_factory=list)
    thumbnail_url: Optional[str] = None
    progress: int = 100
    error: Optional[str] = None
