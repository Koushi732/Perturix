from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CreateProcessingSession(BaseModel):
    id: UUID | None = None
    original_image_name: str
    original_image_hash: str
    image_width: int
    image_height: int
    image_format: str
    status: str = "created"


class AttackResponse(BaseModel):
    id: UUID
    session_id: UUID
    attack_name: str
    attack_version: str
    epsilon: float | None
    execution_time_ms: float | None
    device: str
    success: bool
    parameters: dict[str, Any] | None
    verification_data: dict[str, Any] | None = None

    model_config = ConfigDict(from_attributes=True)


class EvaluationResponse(BaseModel):
    id: UUID
    session_id: UUID
    
    psnr: float | None
    ssim: float | None
    lpips: float | None
    
    l0: float | None
    l2: float | None
    linf: float | None
    
    confidence_before: float | None
    confidence_after: float | None
    confidence_drop: float | None
    attack_success: bool | None
    
    runtime_ms: float | None
    memory_usage_mb: float | None
    
    extra_metrics: dict[str, Any] | None

    model_config = ConfigDict(from_attributes=True)


class ProcessingSessionResponse(BaseModel):
    id: UUID
    created_at: datetime
    updated_at: datetime
    status: str
    original_image_name: str
    original_image_hash: str
    image_width: int
    image_height: int
    image_format: str
    
    attacks: list[AttackResponse] = Field(default_factory=list)
    evaluations: list[EvaluationResponse] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class HistoryResponse(BaseModel):
    items: list[ProcessingSessionResponse]
    total: int
    skip: int
    limit: int


class SearchRequest(BaseModel):
    status: str | None = None
    image_hash: str | None = None
    skip: int = 0
    limit: int = 100
