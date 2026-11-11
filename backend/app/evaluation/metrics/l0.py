from typing import Any

import torch

from app.evaluation.base import BaseMetric
from app.evaluation.context import EvaluationContext
from app.evaluation.exceptions import MetricExecutionException

from .common import validate_tensor_metrics


class L0Metric(BaseMetric):
    @property
    def name(self) -> str:
        return "L0"
        
    @property
    def version(self) -> str:
        return "1.0.0"
        
    def validate(self, context: EvaluationContext) -> None:
        validate_tensor_metrics(context)
            
    def compute(self, context: EvaluationContext) -> float | bool | dict[str, Any] | None:
        try:
            diff = torch.abs(context.original_tensor - context.adversarial_tensor)
            # Threshold chosen to ignore tiny float discrepancies
            return float((diff > 1e-5).sum().item())
        except Exception as e:
            raise MetricExecutionException(f"L0 computation failed: {e}") from e
