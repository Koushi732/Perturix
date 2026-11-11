from typing import Protocol, runtime_checkable

import torch


@runtime_checkable
class IVictimModel(Protocol):
    """
    Abstract interface for victim models to ensure decoupling from concrete PyTorch models.
    """
    
    @property
    def device(self) -> torch.device:
        """Return the primary device the model is located on."""
        ...

    def forward(self, tensor: torch.Tensor) -> torch.Tensor:
        """Perform a forward pass returning raw logits."""
        ...

    def predict(self, tensor: torch.Tensor) -> torch.Tensor:
        """Perform a prediction returning probabilities or class indices."""
        ...

    def compute_gradients(self, tensor: torch.Tensor, *args, **kwargs) -> torch.Tensor:
        """
        Compute and return the gradients of the loss with respect to the input tensor.
        The implementation should handle the forward pass, loss calculation, and backward pass.
        """
        ...

    def zero_grad(self) -> None:
        """Safely clear gradients for the model."""
        ...
