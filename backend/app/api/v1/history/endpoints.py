import uuid
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.dependencies.history import get_history_service
from app.history.schemas import SearchRequest
from app.history.service import HistoryService
from app.middleware.request_context import request_id_var
from app.schemas.common.response import StandardResponse

router = APIRouter(prefix="/history", tags=["History"])

@router.get("/", response_model=StandardResponse)
async def list_history(
    status: str | None = None,
    image_hash: str | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),  # noqa: B008
    history_service: HistoryService = Depends(get_history_service)  # noqa: B008
):
    req = SearchRequest(status=status, image_hash=image_hash, skip=skip, limit=limit)
    res = history_service.search_history(db, req)
    
    return StandardResponse(
        success=True,
        message="History retrieved successfully",
        data=res.model_dump(mode="json"),
        metadata={"request_id": request_id_var.get("SYSTEM")},
        timestamp=datetime.now(UTC).isoformat(),
        request_id=request_id_var.get("SYSTEM")
    )

@router.get("/{session_id}", response_model=StandardResponse)
async def get_session(
    session_id: uuid.UUID,
    db: Session = Depends(get_db),  # noqa: B008
    history_service: HistoryService = Depends(get_history_service)  # noqa: B008
):
    session = history_service.get_session(db, session_id)
    return StandardResponse(
        success=True,
        message="Session retrieved",
        data=session.model_dump(mode="json"),
        metadata={"request_id": request_id_var.get("SYSTEM")},
        timestamp=datetime.now(UTC).isoformat(),
        request_id=request_id_var.get("SYSTEM")
    )

@router.delete("/{session_id}", response_model=StandardResponse)
async def delete_session(
    session_id: uuid.UUID,
    db: Session = Depends(get_db),  # noqa: B008
    history_service: HistoryService = Depends(get_history_service)  # noqa: B008
):
    history_service.session_repo.delete(db, id=session_id)
    return StandardResponse(
        success=True,
        message="Session deleted successfully",
        data=None,
        metadata={"request_id": request_id_var.get("SYSTEM")},
        timestamp=datetime.now(UTC).isoformat(),
        request_id=request_id_var.get("SYSTEM")
    )
