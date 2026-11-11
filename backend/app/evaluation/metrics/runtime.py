from typing import Any

from app.evaluation.base import BaseMetric
from app.evaluation.context import EvaluationContext
from app.evaluation.exceptions import MetricValidationException


class RuntimeMetric(BaseMetric):
    @property
    def name(self) -> str:
        return "Runtime"
        
    @property
    def version(self) -> str:
        return "1.0.0"
        
    def validate(self, context: EvaluationContext) -> None:
        if context.attack_execution_time_ms is None:
            raise MetricValidationException("Runtime not provided in context.")
            
    def compute(self, context: EvaluationContext) -> float | bool | dict[str, Any] | None:
        return context.attack_execution_time_ms
