from typing import Any

import torch

from app.evaluation.base import BaseMetric
from app.evaluation.context import EvaluationContext
from app.evaluation.exceptions import MetricExecutionException

from .common import validate_tensor_metrics


class L2Metric(BaseMetric):
    @property
    def name(self) -> str:
        return "L2"
        
    @property
    def version(self) -> str:
        return "1.0.0"
        
    def validate(self, context: EvaluationContext) -> None:
        validate_tensor_metrics(context)
            
    def compute(self, context: EvaluationContext) -> float | bool | dict[str, Any] | None:
        try:
            diff = context.original_tensor.float() - context.adversarial_tensor.float()
            return float(torch.norm(diff, p=2).item())
        except Exception as e:
            raise MetricExecutionException(f"L2 computation failed: {e}") from e
