from dataclasses import dataclass

import torch

from app.domain.interfaces.model import IVictimModel


@dataclass
class EvaluationContext:
    original_tensor: torch.Tensor
    adversarial_tensor: torch.Tensor
    model: IVictimModel | None = None
    original_probabilities: torch.Tensor | None = None
    adversarial_probabilities: torch.Tensor | None = None
    target_class: int | None = None
    
    # Measured externally (e.g., by the Pipeline or Engine) and consumed by metrics
    attack_execution_time_ms: float | None = None
    attack_memory_usage_mb: float | None = None
