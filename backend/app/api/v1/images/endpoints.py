import os
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, File, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.exceptions import PerturixException
from app.database.session import get_db
from app.dependencies.storage import get_storage_provider
from app.dependencies.workflow import get_workflow_service
from app.middleware.request_context import request_id_var
from app.schemas.common.response import StandardResponse
from app.services.workflow import AttackWorkflowService

router = APIRouter(prefix="/images", tags=["Images"])

@router.post("/upload", response_model=StandardResponse)
async def upload_image(
    image: UploadFile = File(...),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
    workflow: AttackWorkflowService = Depends(get_workflow_service)  # noqa: B008
):
    session = await workflow.handle_upload(db, image)
    
    return StandardResponse(
        success=True,
        message="Image uploaded successfully",
        data=session.model_dump(mode="json"),
        metadata={"request_id": request_id_var.get("SYSTEM")},
        timestamp=datetime.now(UTC).isoformat(),
        request_id=request_id_var.get("SYSTEM")
    )

@router.get("/{filename}")
async def get_image(filename: str):
    storage = get_storage_provider()
    # Assumes LocalStorage for direct FileResponse support in this milestone
    base_dir = getattr(storage, "upload_dir", "storage")
    path = os.path.join(base_dir, filename)
    if not os.path.exists(path):
        raise PerturixException(status_code=404, detail="Image not found", error_code="NOT_FOUND")
    return FileResponse(path)
