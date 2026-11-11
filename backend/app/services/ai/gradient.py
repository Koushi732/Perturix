import torch

from app.core.exceptions import AttackExecutionException, AttackValidationException
from app.domain.interfaces.model import IVictimModel


class GradientService:
    """Service to handle model gradient computations safely and generically."""

    @staticmethod
    def validate_tensor_for_gradients(tensor: torch.Tensor) -> None:
        """Validates that a tensor is ready for gradient computation."""
        if not isinstance(tensor, torch.Tensor):
            raise AttackValidationException("Input must be a PyTorch tensor.")
        if not tensor.is_floating_point():
            raise AttackValidationException("Tensor must be of floating point dtype to compute gradients.")
        if not tensor.requires_grad:
            raise AttackValidationException("Tensor must have requires_grad=True to compute gradients.")

    @staticmethod
    def validate_computed_gradients(grad: torch.Tensor | None, original_tensor: torch.Tensor) -> None:
        """Validates computed gradients for correctness and stability."""
        if grad is None:
            raise AttackExecutionException("Model failed to compute gradients. Gradient is None.")
        if not isinstance(grad, torch.Tensor):
            raise AttackExecutionException("Computed gradient is not a PyTorch tensor.")
        if grad.shape != original_tensor.shape:
            raise AttackExecutionException(f"Gradient shape mismatch. Expected {original_tensor.shape}, got {grad.shape}.")
        if grad.dtype != original_tensor.dtype:
            raise AttackExecutionException(f"Gradient dtype mismatch. Expected {original_tensor.dtype}, got {grad.dtype}.")
        if grad.device != original_tensor.device:
            raise AttackExecutionException(f"Gradient device mismatch. Expected {original_tensor.device}, got {grad.device}.")
        if torch.isnan(grad).any() or torch.isinf(grad).any():
            raise AttackExecutionException("Computed gradient contains NaN or Inf values.")

    def compute_gradients(self, model: IVictimModel, tensor: torch.Tensor, *args, **kwargs) -> torch.Tensor:
        """
        Computes gradients for the given tensor using the model.
        """
        self.validate_tensor_for_gradients(tensor)
        
        try:
            grad = model.compute_gradients(tensor, *args, **kwargs)
        except Exception as e:
            if isinstance(e, AttackExecutionException):
                raise
            raise AttackExecutionException(f"Model raised an error during gradient computation: {e!s}") from e
            
        self.validate_computed_gradients(grad, tensor)
        return grad

    def zero_gradients(self, model: IVictimModel) -> None:
        """
        Safely clears gradients from the model.
        """
        try:
            model.zero_grad()
        except Exception as e:
            raise AttackExecutionException(f"Model raised an error while clearing gradients: {e!s}") from e
