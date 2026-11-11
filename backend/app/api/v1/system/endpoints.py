from datetime import UTC, datetime

from fastapi import APIRouter

from app.config.settings import settings
from app.schemas.common.response import StandardResponse

router = APIRouter(prefix="/system", tags=["System"])

def create_success_response(data: dict) -> StandardResponse:
    from app.middleware.request_context import request_id_var
    return StandardResponse(
        success=True,
        message="Success",
        data=data,
        metadata={"request_id": request_id_var.get("SYSTEM")},
        timestamp=datetime.now(UTC).isoformat(),
        request_id=request_id_var.get("SYSTEM")
    )

@router.get("/health", response_model=StandardResponse)
async def health_check():
    return create_success_response({"status": "ok"})

@router.get("/info", response_model=StandardResponse)
async def system_info():
    return create_success_response({
        "app_name": settings.app_name,
        "environment": settings.environment
    })

@router.get("/version", response_model=StandardResponse)
async def system_version():
    return create_success_response({
        "application_version": settings.version,
        "api_version": "v1",
        "build": "unknown"
    })

@router.get("/status", response_model=StandardResponse)
async def system_status():
    return create_success_response({
        "status": "operational",
        "storage": "connected",
        "ai_registry": "ready"
    })
