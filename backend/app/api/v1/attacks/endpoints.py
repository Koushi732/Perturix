import uuid
from datetime import UTC, datetime
from typing import Any

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

router = APIRouter(prefix="/attacks", tags=["Attacks"])

class ExecuteAttackRequest(BaseModel):
    session_id: uuid.UUID
    attack_name: str
    parameters: dict[str, Any] = {}

@router.post("/execute", response_model=StandardResponse)
async def execute_attack(
    request: ExecuteAttackRequest,
    db: Session = Depends(get_db),  # noqa: B008
    workflow: AttackWorkflowService = Depends(get_workflow_service)  # noqa: B008
):
    attack_res = await workflow.execute_attack(
        db,
        session_id=request.session_id,
        attack_name=request.attack_name,
        parameters=request.parameters
    )
    
    return StandardResponse(
        success=True,
        message="Attack executed successfully",
        data=attack_res.model_dump(mode="json"),
        metadata={"request_id": request_id_var.get("SYSTEM")},
        timestamp=datetime.now(UTC).isoformat(),
        request_id=request_id_var.get("SYSTEM")
    )

@router.get("/{session_id}", response_model=StandardResponse)
async def get_attacks(
    session_id: uuid.UUID,
    db: Session = Depends(get_db),  # noqa: B008
    history_service: HistoryService = Depends(get_history_service)  # noqa: B008
):
    session = history_service.get_session(db, session_id)
    return StandardResponse(
        success=True,
        message="Attacks retrieved",
        data=[a.model_dump(mode="json") for a in session.attacks],
        metadata={"request_id": request_id_var.get("SYSTEM")},
        timestamp=datetime.now(UTC).isoformat(),
        request_id=request_id_var.get("SYSTEM")
    )
