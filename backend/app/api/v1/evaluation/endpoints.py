import uuid
from datetime import UTC, datetime

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.dependencies.history import get_history_service
from app.dependencies.workflow import get_workflow_service
from app.history.service import HistoryService
from app.middleware.request_context import request_id_var
from app.schemas.common.response import StandardResponse
from app.services.workflow import AttackWorkflowService

router = APIRouter(prefix="/evaluation", tags=["Evaluation"])

class ExecuteEvaluationRequest(BaseModel):
    session_id: uuid.UUID

@router.post("/execute", response_model=StandardResponse)
async def execute_evaluation(
    request: ExecuteEvaluationRequest,
    db: Session = Depends(get_db),  # noqa: B008
    workflow: AttackWorkflowService = Depends(get_workflow_service)  # noqa: B008
):
    eval_res = await workflow.evaluate_session(db, session_id=request.session_id)
    
    return StandardResponse(
        success=True,
        message="Evaluation completed successfully",
        data=eval_res.model_dump(mode="json"),
        metadata={"request_id": request_id_var.get("SYSTEM")},
        timestamp=datetime.now(UTC).isoformat(),
        request_id=request_id_var.get("SYSTEM")
    )

@router.get("/{session_id}", response_model=StandardResponse)
async def get_evaluation(
    session_id: uuid.UUID,
    db: Session = Depends(get_db),  # noqa: B008
    history_service: HistoryService = Depends(get_history_service)  # noqa: B008
):
    session = history_service.get_session(db, session_id)
    return StandardResponse(
        success=True,
        message="Evaluations retrieved",
        data=[e.model_dump(mode="json") for e in session.evaluations],
        metadata={"request_id": request_id_var.get("SYSTEM")},
        timestamp=datetime.now(UTC).isoformat(),
        request_id=request_id_var.get("SYSTEM")
    )
