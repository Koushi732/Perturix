import time
from typing import Any

import torch

from app.ai_engine.base import BaseAttack
from app.ai_engine.models import AttackResult
from app.core.exceptions import AttackExecutionException, AttackValidationException
from app.domain.interfaces.model import IVictimModel
from app.services.ai.gradient import GradientService

from .config import FGSMConfig


class FGSMAttack(BaseAttack):
    def __init__(self, config: FGSMConfig | None = None):
        self._config = config or FGSMConfig()
        self._gradient_service = GradientService()
        self._tensor: torch.Tensor | None = None
        self._model: IVictimModel | None = None

    @property
    def name(self) -> str:
        return self._config.name

    @property
    def version(self) -> str:
        return self._config.version

    def initialize(self) -> None:
        """FGSM does not require stateful initialization."""

    def validate(self, inputs: dict[str, Any]) -> None:
        if "tensor" not in inputs:
            raise AttackValidationException("Missing 'tensor' in inputs.")
        if "model" not in inputs:
            raise AttackValidationException("Missing 'model' in inputs.")
            
        tensor = inputs["tensor"]
        model = inputs["model"]
        
        if not isinstance(tensor, torch.Tensor):
            raise AttackValidationException("'tensor' must be a PyTorch tensor.")
        if not isinstance(model, IVictimModel):
            raise AttackValidationException("'model' must implement IVictimModel interface.")

        if tensor.ndim < 3:
             raise AttackValidationException("Tensor must have at least 3 dimensions (C, H, W).")
             
        channels = tensor.shape[1] if tensor.ndim == 4 else tensor.shape[0]
        if channels != 3:
             raise AttackValidationException(f"Expected 3 channels (RGB), got {channels}.")
             
        if not tensor.is_floating_point():
             raise AttackValidationException("Tensor must be floating point.")
             
        if torch.isnan(tensor).any() or torch.isinf(tensor).any():
             raise AttackValidationException("Tensor contains NaN or Inf values.")
             
        if not tensor.requires_grad:
             raise AttackValidationException("Tensor requires_grad must be True.")

        # Save for execution
        self._tensor = tensor
        self._model = model

    def execute(self, inputs: dict[str, Any]) -> AttackResult:
        if self._tensor is None or self._model is None:
            raise AttackExecutionException("Attack not validated properly before execution.")
            
        start_time = time.perf_counter()
        
        try:
            # 1. Get Gradients
            target_class = inputs.get("target_class")
            grad = self._gradient_service.compute_gradients(self._model, self._tensor, target_class=target_class)
            
            # 2. FGSM Equation: x_adv = x + epsilon * sign(grad)
            # Create a new tensor (no in-place ops)
            perturbation = self._config.epsilon * torch.sign(grad)
            x_adv = self._tensor + perturbation
            
            # 3. Clamp
            x_adv = torch.clamp(x_adv, min=self._config.clamp_min, max=self._config.clamp_max)
            
            # Ensure shape and dtype are preserved
            if x_adv.shape != self._tensor.shape:
                 raise AttackExecutionException("Output tensor shape mismatch.")
            if x_adv.dtype != self._tensor.dtype:
                 x_adv = x_adv.to(self._tensor.dtype)
                 
            execution_time = (time.perf_counter() - start_time) * 1000
            
            image_size = (x_adv.shape[-2], x_adv.shape[-1])
            
            metadata = {
                "epsilon": self._config.epsilon,
                "device": str(x_adv.device),
                "execution_time_ms": execution_time,
                "tensor_shape": list(x_adv.shape),
                "dtype": str(x_adv.dtype),
                "image_size": image_size,
                "attack_version": self.version
            }
            
            artifacts = {
                "adversarial_tensor": x_adv
            }
            
            return AttackResult(
                attack_name=self.name,
                success=True,
                execution_time_ms=execution_time,
                original_metadata={},
                protected_metadata=metadata,
                artifacts=artifacts,
                warnings=[],
                errors=[]
            )
            
        except Exception as e:
            if isinstance(e, AttackExecutionException):
                raise
            raise AttackExecutionException(f"FGSM execution failed: {e!s}") from e

    def cleanup(self) -> None:
        if self._model is not None:
            self._gradient_service.zero_gradients(self._model)
        self._tensor = None
        self._model = None
