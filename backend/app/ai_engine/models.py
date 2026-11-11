from typing import Any

from pydantic import BaseModel


class AttackResult(BaseModel):
    attack_name: str
    success: bool
    execution_time_ms: float
    original_metadata: dict[str, Any]
    protected_metadata: dict[str, Any]
    artifacts: dict[str, Any] = {}
    metrics: dict[str, float] | None = None
    warnings: list[str] = []
    errors: list[str] = []
