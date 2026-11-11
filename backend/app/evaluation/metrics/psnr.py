from typing import Any

from torchmetrics.image import PeakSignalNoiseRatio

from app.evaluation.base import BaseMetric
from app.evaluation.context import EvaluationContext
from app.evaluation.exceptions import MetricExecutionException

from .common import validate_tensor_metrics


class PSNRMetric(BaseMetric):
    @property
    def name(self) -> str:
        return "PSNR"
        
    def __init__(self) -> None:
        self.metric: Any = None

    @property
    def version(self) -> str:
        return "1.0.0"
        
    def initialize(self) -> None:
        self.metric = PeakSignalNoiseRatio(data_range=255.0)
        
    def validate(self, context: EvaluationContext) -> None:
        validate_tensor_metrics(context)
            
    def compute(self, context: EvaluationContext) -> float | bool | dict[str, Any] | None:
        try:
            # torchmetrics usually expects (preds, target) where preds = adv, target = orig
            val = self.metric(context.adversarial_tensor, context.original_tensor)
            return float(val.item())
        except Exception as e:
            raise MetricExecutionException(f"PSNR computation failed: {e}") from e
            
    def cleanup(self) -> None:
        self.metric = None
