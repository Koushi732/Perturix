from typing import Any

import torch

from app.evaluation.base import BaseMetric
from app.evaluation.context import EvaluationContext
from app.evaluation.exceptions import (
    MetricExecutionException,
    MetricValidationException,
)


class ConfidenceMetric(BaseMetric):
    @property
    def name(self) -> str:
        return "Confidence"
        
    @property
    def version(self) -> str:
        return "1.0.0"
        
    def validate(self, context: EvaluationContext) -> None:
        if context.original_probabilities is None or context.adversarial_probabilities is None:
            raise MetricValidationException("Original and adversarial probabilities are required.")
        if context.original_probabilities.shape != context.adversarial_probabilities.shape:
            raise MetricValidationException("Probabilities shape mismatch.")
        if torch.isnan(context.original_probabilities).any() or torch.isinf(context.original_probabilities).any():
            raise MetricValidationException("Original probabilities contain NaN or Inf.")
        if torch.isnan(context.adversarial_probabilities).any() or torch.isinf(context.adversarial_probabilities).any():
            raise MetricValidationException("Adversarial probabilities contain NaN or Inf.")
            
    def compute(self, context: EvaluationContext) -> float | bool | dict[str, Any] | None:
        try:
            orig = context.original_probabilities
            adv = context.adversarial_probabilities
            assert orig is not None and adv is not None
            
            target = context.target_class
            if target is None:
                # Assuming shape (B, C)
                target = int(torch.argmax(orig, dim=-1)[0].item())
                
            conf_before = float(orig[0, target].item())
            conf_after = float(adv[0, target].item())
            conf_drop = conf_before - conf_after
            
            success = bool(torch.argmax(orig, dim=-1)[0].item() != torch.argmax(adv, dim=-1)[0].item())
            
            return {
                "confidence_before": conf_before,
                "confidence_after": conf_after,
                "confidence_drop": conf_drop,
                "attack_success": success
            }
        except Exception as e:
            raise MetricExecutionException(f"Confidence computation failed: {e}") from e
