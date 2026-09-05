"""
FastAPI REST API Routes for Agent 6 (Response Evaluation + Adaptive Teaching).
Conforms to Section 39.
"""

from typing import Optional, Dict, Any, List
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from backend.evaluation.schemas import (
    StudentResponse,
    QuestionContext,
    EvaluationResult,
    AdaptationDecision,
    LearningEvidence,
)
from backend.evaluation.services import evaluation_service

router = APIRouter(prefix="/evaluation", tags=["Response Evaluation & Adaptive Teaching (Agent 6)"])


class EvaluationRequest(BaseModel):
    student_response: StudentResponse
    question_context: QuestionContext
    learner_context: Optional[Dict[str, Any]] = None
    student_id: Optional[str] = None
    submit_to_agent3: bool = False


class EvaluationResponse(BaseModel):
    status: str = "success"
    evaluation: EvaluationResult
    adaptation: AdaptationDecision
    learning_evidence: LearningEvidence


class BatchEvaluationRequest(BaseModel):
    items: List[EvaluationRequest]


class BatchEvaluationResponse(BaseModel):
    status: str = "success"
    total_evaluated: int
    results: List[EvaluationResponse]


@router.post("/respond", response_model=EvaluationResponse)
async def evaluate_student_response(payload: EvaluationRequest):
    """
    Primary endpoint: Evaluates a student response against question context,
    diagnoses misconceptions/knowledge gaps, and generates adaptation recommendations.
    """
    try:
        evaluation, adaptation, evidence = evaluation_service.evaluate_and_adapt(
            response=payload.student_response,
            question=payload.question_context,
            learner_context=payload.learner_context,
            student_id=payload.student_id,
            auto_submit_to_agent3=payload.submit_to_agent3
        )
        return EvaluationResponse(
            status="success",
            evaluation=evaluation,
            adaptation=adaptation,
            learning_evidence=evidence
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Evaluation failed: {str(e)}")


@router.post("/batch", response_model=BatchEvaluationResponse)
async def batch_evaluate_responses(payload: BatchEvaluationRequest):
    """
    Evaluates a batch of student responses for multi-question assessments.
    """
    results = []
    for item in payload.items:
        try:
            evaluation, adaptation, evidence = evaluation_service.evaluate_and_adapt(
                response=item.student_response,
                question=item.question_context,
                learner_context=item.learner_context,
                student_id=item.student_id,
                auto_submit_to_agent3=item.submit_to_agent3
            )
            results.append(EvaluationResponse(
                status="success",
                evaluation=evaluation,
                adaptation=adaptation,
                learning_evidence=evidence
            ))
        except Exception as e:
            # Continue evaluating remaining items
            continue

    return BatchEvaluationResponse(
        status="success",
        total_evaluated=len(results),
        results=results
    )


@router.get("/{evaluation_id}", response_model=EvaluationResult)
async def get_evaluation_by_id(evaluation_id: str):
    """
    Retrieves a previously computed evaluation by ID.
    """
    eval_res = evaluation_service.get_evaluation(evaluation_id)
    if not eval_res:
        raise HTTPException(status_code=404, detail=f"Evaluation '{evaluation_id}' not found")
    return eval_res


@router.get("/session/{session_id}", response_model=List[EvaluationResult])
async def get_session_evaluations(session_id: str):
    """
    Retrieves all evaluations for a specific teaching session.
    """
    return evaluation_service.get_session_evaluations(session_id)
