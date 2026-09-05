"""
Video Generation API Routes (Agent 4)
Exposes REST endpoints conforming to Sections 38, 39, 40 of Agent 4 specification:
- POST /api/video/generate
- GET  /api/video/{video_id}
- GET  /api/video/{video_id}/scenes
- POST /api/video/render-scene
- POST /api/video/step
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field

from backend.video.schemas import VideoLesson, VideoScene, VideoStatus
from backend.video.service import video_service

router = APIRouter(prefix="/video", tags=["Video Engine"])


class GenerateVideoRequest(BaseModel):
    session_id: Optional[str] = "session_001"
    lesson_id: Optional[str] = "lesson_001"
    title: Optional[str] = "Educational Video Lesson"
    language: Optional[str] = "Hinglish"
    mode: Optional[str] = "batch"  # "batch" or "interactive"
    teaching_steps: List[Dict[str, Any]] = Field(default_factory=list)
    # Flat single-step payload support for integration backward compatibility
    step_id: Optional[str] = None
    spoken_text: Optional[str] = None
    visual_type: Optional[str] = None


class RenderSceneRequest(BaseModel):
    scene_id: Optional[str] = None
    visual: Dict[str, Any] = Field(default_factory=dict)
    spoken_text: Optional[str] = ""


@router.post("/generate")
async def generate_lesson_video(request: GenerateVideoRequest):
    """
    POST /api/video/generate (Section 38 & 40)
    Batch video generation for a sequence of TeachingSteps.
    Also handles single-step generation requests seamlessly.
    """
    try:
        steps = request.teaching_steps
        if not steps and (request.step_id or request.spoken_text):
            steps = [{
                "step_id": request.step_id or "step_01",
                "step_type": "explanation",
                "explanation": request.spoken_text or "Educational explanation",
                "spoken_script": request.spoken_text or "Educational explanation",
                "language": request.language or "Hinglish",
                "visual_instruction": {
                    "type": request.visual_type or "circuit",
                    "title": "Educational Visual"
                }
            }]

        lesson = video_service.generate_lesson_video(
            session_id=request.session_id or "session_001",
            lesson_id=request.lesson_id or "lesson_001",
            teaching_steps=steps,
            title=request.title or "Educational Video Lesson",
            language=request.language or "Hinglish",
            mode=request.mode or "batch"
        )

        first_scene = lesson.scenes[0] if lesson.scenes else None
        scene_id = first_scene.scene_id if first_scene else f"scene_{request.step_id or '01'}"

        return {
            "status": "success",
            "video_id": lesson.video_lesson_id,
            "video_lesson_id": lesson.video_lesson_id,
            "video_status": lesson.status,
            "duration_seconds": lesson.duration_seconds,
            "video_url": lesson.video_url or (first_scene.frame_url if first_scene else "/media/video.mp4"),
            "thumbnail_url": lesson.thumbnail_url,
            "scenes_count": len(lesson.scenes),
            "scene_id": scene_id,
            "step_id": request.step_id or (first_scene.step_id if first_scene else "step_01"),
            "visual_type": request.visual_type or "circuit",
            "ready": True
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate video lesson: {str(e)}")


@router.get("/{video_id}")
async def get_video_status(video_id: str):
    """
    GET /api/video/{video_id} (Section 38)
    Returns generation status and metadata for a video.
    """
    lesson = video_service.get_video_lesson(video_id)
    if not lesson:
        raise HTTPException(status_code=404, detail=f"Video with id '{video_id}' not found.")
    
    return {
        "status": "success",
        "video_id": lesson.video_lesson_id,
        "video_status": lesson.status,
        "progress": lesson.progress,
        "duration_seconds": lesson.duration_seconds,
        "video_url": lesson.video_url,
        "thumbnail_url": lesson.thumbnail_url,
        "resolution": lesson.resolution,
        "created_at": lesson.created_at
    }


@router.get("/{video_id}/scenes")
async def get_video_scenes(video_id: str):
    """
    GET /api/video/{video_id}/scenes (Section 38)
    Returns full scene sequence metadata for the video.
    """
    scenes = video_service.get_video_scenes(video_id)
    if scenes is None:
        raise HTTPException(status_code=404, detail=f"Video with id '{video_id}' not found.")
    
    return {
        "status": "success",
        "video_id": video_id,
        "scenes_count": len(scenes),
        "scenes": [s.model_dump() for s in scenes]
    }


@router.post("/step")
async def render_step_video(payload: Dict[str, Any]):
    """
    POST /api/video/step (Section 39)
    Interactive mode: Generates synchronized VideoScene(s) for a single TeachingStep.
    Supports incremental teaching with pause-on-question semantics.
    """
    try:
        scenes = video_service.render_teaching_step(payload, mode="interactive")
        return {
            "status": "success",
            "scenes_count": len(scenes),
            "scenes": [s.model_dump() for s in scenes],
            "first_scene": scenes[0].model_dump() if scenes else None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to render step video: {str(e)}")


@router.post("/render-scene")
async def render_scene_debug(request: RenderSceneRequest):
    """
    POST /api/video/render-scene (Section 38)
    Development/debug endpoint to render a standalone visual spec into a frame.
    """
    try:
        result = video_service.render_single_scene_debug(request.model_dump())
        return {
            "status": "success",
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to render scene: {str(e)}")
