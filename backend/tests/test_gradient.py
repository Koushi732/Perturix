import pytest
import torch

from app.core.exceptions import AttackExecutionException, AttackValidationException
from app.services.ai.gradient import GradientService


class MockModel:
    def __init__(self, grad_shape=None, grad_dtype=None, device=None, return_none=False, nan_inf=False):
        self.grad_shape = grad_shape
        self.grad_dtype = grad_dtype
        self._device = device or torch.device("cpu")
        self.return_none = return_none
        self.nan_inf = nan_inf
        self.zero_grad_called = False

    @property
    def device(self) -> torch.device:
        return self._device

    def forward(self, tensor: torch.Tensor) -> torch.Tensor:
        return tensor

    def predict(self, tensor: torch.Tensor) -> torch.Tensor:
        return tensor

    def compute_gradients(self, tensor: torch.Tensor, *args, **kwargs) -> torch.Tensor:
        if self.return_none:
            return None  # type: ignore
        grad = torch.ones(self.grad_shape or tensor.shape, dtype=self.grad_dtype or tensor.dtype, device=self.device)
        if self.nan_inf:
            grad[0, 0, 0] = float('nan')
        return grad

    def zero_grad(self) -> None:
        self.zero_grad_called = True


def test_gradient_validation() -> None:
    service = GradientService()
    
    with pytest.raises(AttackValidationException, match="must be a PyTorch tensor"):
        service.validate_tensor_for_gradients("not a tensor")  # type: ignore
        
    tensor = torch.ones(1, 3, 224, 224, dtype=torch.int32)
    with pytest.raises(AttackValidationException, match="floating point dtype"):
        service.validate_tensor_for_gradients(tensor)
        
    tensor = torch.ones(1, 3, 224, 224)
    with pytest.raises(AttackValidationException, match="requires_grad=True"):
        service.validate_tensor_for_gradients(tensor)
        

def test_gradient_computation_success() -> None:
    service = GradientService()
    model = MockModel()
    tensor = torch.ones(1, 3, 224, 224, requires_grad=True)
    
    grad = service.compute_gradients(model, tensor)  # type: ignore
    assert grad.shape == tensor.shape


def test_gradient_computation_failures() -> None:
    service = GradientService()
    tensor = torch.ones(1, 3, 224, 224, requires_grad=True)
    
    # None gradient
    with pytest.raises(AttackExecutionException, match="Gradient is None"):
        service.compute_gradients(MockModel(return_none=True), tensor)  # type: ignore
        
    # Non-tensor gradient
    class BadGradModel(MockModel):
        def compute_gradients(self, tensor, *args, **kwargs):
            return "not a tensor"
    with pytest.raises(AttackExecutionException, match="not a PyTorch tensor"):
        service.compute_gradients(BadGradModel(), tensor)  # type: ignore
        
    # Shape mismatch
    with pytest.raises(AttackExecutionException, match="Gradient shape mismatch"):
        service.compute_gradients(MockModel(grad_shape=(1, 3, 224, 225)), tensor)  # type: ignore
        
    # Dtype mismatch
    with pytest.raises(AttackExecutionException, match="Gradient dtype mismatch"):
        service.compute_gradients(MockModel(grad_dtype=torch.float64), tensor)  # type: ignore
        
    # Device mismatch
    with pytest.raises(AttackExecutionException, match="Gradient device mismatch"):
        service.compute_gradients(MockModel(device=torch.device("meta")), tensor)  # type: ignore
        
    # NaN/Inf
    with pytest.raises(AttackExecutionException, match="NaN or Inf"):
        service.compute_gradients(MockModel(nan_inf=True), tensor)  # type: ignore
        
    # Exception during computation
    class ThrowingModel(MockModel):
        def compute_gradients(self, tensor, *args, **kwargs):
            raise RuntimeError("Model failed")
    with pytest.raises(AttackExecutionException, match="Model failed"):
        service.compute_gradients(ThrowingModel(), tensor)  # type: ignore
        
def test_zero_gradients_exception() -> None:
    service = GradientService()
    class ThrowingZeroModel(MockModel):
        def zero_grad(self):
            raise RuntimeError("Failed to zero")
    with pytest.raises(AttackExecutionException, match="Failed to zero"):
        service.zero_gradients(ThrowingZeroModel())
