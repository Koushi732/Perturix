from pydantic import BaseModel, ConfigDict
from typing import Any
import torch

class VerificationStats(BaseModel):
    coverage: float
    strength: float
    entropy: float
    density: float
    gradient_consistency: float
    verification_score: float
    status: str

class PerturbationResult(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    adversarial_tensor: torch.Tensor
    perturbation_tensor: torch.Tensor
    verification: VerificationStats
    heatmap_filename: str | None = None
    difference_filename: str | None = None
    overlay_filename: str | None = None
    perturbation_filename: str | None = None
