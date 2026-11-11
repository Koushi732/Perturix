from dataclasses import dataclass

import torch


@dataclass
class PreprocessingOutput:
    """Dedicated object returned by the preprocessing pipeline."""
    tensor: torch.Tensor
    width: int
    height: int
    channels: int
    normalized: bool
    processing_time_ms: float
