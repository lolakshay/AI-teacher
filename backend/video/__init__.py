"""
AI Teaching Video Engine (Agent 4)
Converts structured educational TeachingStep objects into a video-ready representation
and generated educational video lessons.
"""

from backend.video.schemas import (
    VideoLesson,
    VideoScene,
    VisualSpec,
    EquationVisualSpec,
    GraphVisualSpec,
    CodeVisualSpec,
    TimelineVisualSpec,
    MapVisualSpec,
    ProcessVisualSpec,
    ImageVisualSpec,
    WorkedExampleVisualSpec,
    ConceptCardVisualSpec,
    VideoStatus,
    RenderedVideo
)

__all__ = [
    "VideoLesson",
    "VideoScene",
    "VisualSpec",
    "EquationVisualSpec",
    "GraphVisualSpec",
    "CodeVisualSpec",
    "TimelineVisualSpec",
    "MapVisualSpec",
    "ProcessVisualSpec",
    "ImageVisualSpec",
    "WorkedExampleVisualSpec",
    "ConceptCardVisualSpec",
    "VideoStatus",
    "RenderedVideo"
]
