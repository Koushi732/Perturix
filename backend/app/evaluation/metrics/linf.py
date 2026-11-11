from typing import Any

import torch

from app.evaluation.base import BaseMetric
from app.evaluation.context import EvaluationContext
from app.evaluation.exceptions import MetricExecutionException

from .common import validate_tensor_metrics


class LinfMetric(BaseMetric):
    @property
    def name(self) -> str:
        return "Linf"
        
    @property
    def version(self) -> str:
        return "1.0.0"
        
    def validate(self, context: EvaluationContext) -> None:
        validate_tensor_metrics(context)
            
    def compute(self, context: EvaluationContext) -> float | bool | dict[str, Any] | None:
        try:
            diff = context.original_tensor.float() - context.adversarial_tensor.float()
            return float(torch.norm(diff, p=float('inf')).item())
        except Exception as e:
            raise MetricExecutionException(f"Linf computation failed: {e}") from e
