"""
Assessment REST API Routes conforming to Section 44.
Endpoints for creating assessments, conducting student sessions, scoring,
retrieving detailed learning analytics and generating comprehensive reports.
"""

from typing import Optional, Dict, Any, List
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from backend.assessment.models.config import AssessmentConfig
from backend.assessment.models.session import AssessmentResponse
from backend.assessment.services.assessment_service import (
    assessment_service, AssessmentNotFoundError, SessionNotFoundError
)

router = APIRouter(prefix="/assessment", tags=["Assessment & Analytics (Agent 7)"])


class CreateAssessmentPayload(BaseModel):
    student_id: Optional[str] = "demo_student"
    lesson_id: Optional[str] = None
    topic: str
    question_count: int = 5
    duration_minutes: Optional[int] = None
    question_types: Optional[List[str]] = None
    difficulty: float = 0.4
    coverage: Optional[List[str]] = None
    passing_score: float = 0.70
    language: str = "English"
    randomize: bool = False
    random_seed: Optional[int] = None


class StartSessionPayload(BaseModel):
    student_id: str
    session_id: Optional[str] = None


class ResponsePayload(BaseModel):
    session_id: str
    question_id: str
    answer: str
    is_skipped: bool = False
    time_spent_seconds: Optional[float] = None


class SubmitAssessmentPayload(BaseModel):
    session_id: str
    answers: Optional[Dict[str, str]] = None
    learning_path: Optional[List[str]] = None


class QuickEvaluatePayload(BaseModel):
    topic: str
    student_id: str = "demo_student"
    lesson_id: Optional[str] = None
    answers: Dict[str, str]
    learning_path: Optional[List[str]] = None
    language: str = "English"


@router.post("/create")
async def create_assessment(payload: CreateAssessmentPayload):
    """
    Creates a new formal assessment for a topic and lesson with grounded questions.
    """
    try:
        config = AssessmentConfig(
            lesson_id=payload.lesson_id,
            student_id=payload.student_id,
            topic=payload.topic,
            question_count=payload.question_count,
            duration_minutes=payload.duration_minutes,
            question_types=payload.question_types or ["mcq", "short_answer", "numerical", "conceptual"],
            difficulty=payload.difficulty,
            coverage=payload.coverage or [],
            passing_score=payload.passing_score,
            language=payload.language,
            randomize=payload.randomize,
            random_seed=payload.random_seed
        )
        _, questions = assessment_service.create_assessment(config)
        # Return student sanitized view by default
        sanitized = [q.model_copy(update={"correct_option": None, "expected_answer": None, "expected_value": None, "rubric": []}) for q in questions]
        return {
            "status": "success",
            "assessment_id": config.assessment_id,
            "topic": config.topic,
            "question_count": len(sanitized),
            "questions": sanitized
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to create assessment: {str(e)}")


@router.get("/{assessment_id}")
async def get_assessment(assessment_id: str, student_view: bool = Query(default=True)):
    """
    Retrieves assessment questions and metadata. Answer keys are omitted when student_view=True.
    """
    res = assessment_service.get_assessment(assessment_id, student_view=student_view)
    if not res:
        raise HTTPException(status_code=404, detail=f"Assessment '{assessment_id}' not found.")
    config, questions = res
    return {
        "status": "success",
        "assessment_id": config.assessment_id,
        "config": config,
        "questions": questions
    }


@router.post("/{assessment_id}/start")
async def start_assessment_session(assessment_id: str, payload: StartSessionPayload):
    """
    Starts an active assessment session for a student.
    """
    try:
        session = assessment_service.start_session(
            assessment_id=assessment_id,
            student_id=payload.student_id,
            session_id=payload.session_id
        )
        return {"status": "success", "session": session}
    except AssessmentNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{assessment_id}/response")
async def record_response(assessment_id: str, payload: ResponsePayload):
    """
    Records an individual student response during the active session.
    """
    try:
        resp = AssessmentResponse(
            question_id=payload.question_id,
            student_id="",  # Populated from session
            answer=payload.answer,
            is_skipped=payload.is_skipped,
            time_spent_seconds=payload.time_spent_seconds
        )
        session = assessment_service.submit_response(payload.session_id, resp)
        return {"status": "success", "session": session}
    except SessionNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{assessment_id}/submit")
async def submit_assessment(assessment_id: str, payload: SubmitAssessmentPayload):
    """
    Submits the assessment, runs multi-question scoring and analytics, and generates the learning report.
    """
    try:
        result, report = assessment_service.submit_assessment(
            session_id=payload.session_id,
            answers=payload.answers,
            learning_path=payload.learning_path
        )
        return {
            "status": "success",
            "result": result,
            "report": report
        }
    except (AssessmentNotFoundError, SessionNotFoundError) as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{assessment_id}/result")
async def get_assessment_result(assessment_id: str):
    """
    Retrieves the fine-grained AssessmentResult containing question and concept-level scores.
    """
    res = assessment_service.get_result(assessment_id)
    if not res:
        raise HTTPException(status_code=404, detail=f"No results found for '{assessment_id}'.")
    return {"status": "success", "result": res}


@router.get("/{assessment_id}/report")
async def get_learning_report(assessment_id: str):
    """
    Retrieves the formal LearningReport containing actionable revision, progress, and next topic recommendations.
    """
    report = assessment_service.get_report(assessment_id)
    if not report:
        raise HTTPException(status_code=404, detail=f"No report found for '{assessment_id}'.")
    return {"status": "success", "report": report}


@router.post("/evaluate_quick")
async def evaluate_quick_quiz(payload: QuickEvaluatePayload):
    """
    1-step quick evaluation: creates assessment, grades student answers, and returns report immediately.
    """
    try:
        config = AssessmentConfig(
            topic=payload.topic,
            student_id=payload.student_id,
            lesson_id=payload.lesson_id,
            question_count=len(payload.answers),
            language=payload.language
        )
        _, questions = assessment_service.create_assessment(config)
        result, report = assessment_service.submit_assessment(
            session_id=assessment_service.start_session(config.assessment_id, payload.student_id).session_id,
            answers=payload.answers,
            learning_path=payload.learning_path
        )
        return {
            "status": "success",
            "score": result.score,
            "weak_areas": result.weak_areas,
            "strong_areas": result.strong_areas,
            "misconceptions": result.misconceptions,
            "report": report
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
