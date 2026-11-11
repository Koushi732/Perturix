from typing import Any

from torchmetrics.image.lpip import LearnedPerceptualImagePatchSimilarity

from app.evaluation.base import BaseMetric
from app.evaluation.context import EvaluationContext
from app.evaluation.exceptions import MetricExecutionException

from .common import validate_tensor_metrics


class LPIPSMetric(BaseMetric):
    @property
    def name(self) -> str:
        return "LPIPS"
        
    def __init__(self) -> None:
        self.metric: Any = None

    @property
    def version(self) -> str:
        return "1.0.0"
        
    def initialize(self) -> None:
        # LPIPS with normalize=True expects inputs in [0, 1] and scales them to [-1, 1]
        self.metric = LearnedPerceptualImagePatchSimilarity(net_type='alex', normalize=True)
        
    def validate(self, context: EvaluationContext) -> None:
        validate_tensor_metrics(context)
            
    def compute(self, context: EvaluationContext) -> float | bool | dict[str, Any] | None:
        try:
            orig = context.original_tensor / 255.0
            adv = context.adversarial_tensor / 255.0
            
            # Ensure tensors are contiguous
            orig = orig.contiguous()
            adv = adv.contiguous()
            
            val = self.metric(adv, orig)
            return float(val.item())
        except Exception as e:
            raise MetricExecutionException(f"LPIPS computation failed: {e}") from e
            
    def cleanup(self) -> None:
        self.metric = None
