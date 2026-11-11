import torch

from app.evaluation.context import EvaluationContext
from app.evaluation.exceptions import MetricValidationException


def validate_tensor_metrics(context: EvaluationContext) -> None:
    """Standard validation for image quality and perturbation metrics."""
    if context.original_tensor is None or context.adversarial_tensor is None:
        raise MetricValidationException("Original and adversarial tensors are required.")
    if context.original_tensor.shape != context.adversarial_tensor.shape:
        raise MetricValidationException("Tensor shapes must match.")
    if torch.isnan(context.original_tensor).any() or torch.isinf(context.original_tensor).any():
        raise MetricValidationException("Original tensor contains NaN or Inf.")
    if torch.isnan(context.adversarial_tensor).any() or torch.isinf(context.adversarial_tensor).any():
        raise MetricValidationException("Adversarial tensor contains NaN or Inf.")
    if context.original_tensor.ndim != 4:
        raise MetricValidationException("Expected 4D tensors (B, C, H, W).")
    if context.original_tensor.shape[1] != 3:
        raise MetricValidationException("Expected 3 channels (RGB) for metrics.")
