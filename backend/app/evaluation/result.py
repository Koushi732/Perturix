from datetime import UTC, datetime
from uuid import UUID

from pydantic import BaseModel, Field


class EvaluationResult(BaseModel):
    evaluation_id: UUID
    attack_name: str
    attack_version: str
    image_name: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    
    # Image Quality
    psnr: float | None = None
    ssim: float | None = None
    lpips: float | None = None
    
    # Perturbation
    l0: float | None = None
    l2: float | None = None
    linf: float | None = None
    
    # Attack
    confidence_before: float | None = None
    confidence_after: float | None = None
    confidence_drop: float | None = None
    attack_success: bool | None = None
    
    # Performance
    execution_time_ms: float | None = None
    memory_usage_mb: float | None = None
    
    # Metadata
    warnings: list[str] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)
    evaluator_version: str
    metric_versions: dict[str, str] = Field(default_factory=dict)
