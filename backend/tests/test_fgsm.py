import pytest
import torch

from app.ai_engine.algorithms.fgsm import FGSMAttack, FGSMConfig
from app.core.exceptions import AttackExecutionException, AttackValidationException


class MockVictimModel:
    def __init__(self, grad_value=1.0):
        self._device = torch.device("cpu")
        self.grad_value = grad_value
        self.zero_grad_called = False
        
    @property
    def device(self) -> torch.device:
        return self._device
         
    def forward(self, tensor: torch.Tensor) -> torch.Tensor:
        return tensor
         
    def predict(self, tensor: torch.Tensor) -> torch.Tensor:
        return tensor
         
    def compute_gradients(self, tensor: torch.Tensor, *args, **kwargs) -> torch.Tensor:
        if self.grad_value == 0.0:
            return torch.zeros_like(tensor)
        return torch.full_like(tensor, self.grad_value)
         
    def zero_grad(self) -> None:
        self.zero_grad_called = True


def test_fgsm_success() -> None:
    attack = FGSMAttack(FGSMConfig(epsilon=10.0))
    tensor = torch.ones(1, 3, 224, 224, requires_grad=True) * 100.0
    model = MockVictimModel(grad_value=1.0)
    
    attack.validate({"tensor": tensor, "model": model})
    result = attack.execute({})
    
    assert result.success is True
    assert result.attack_name == "FGSM"
    assert "adversarial_tensor" in result.artifacts
    
    x_adv = result.artifacts["adversarial_tensor"]
    assert x_adv.shape == tensor.shape
    assert x_adv.dtype == tensor.dtype
    
    # Original tensor must be unchanged
    assert torch.all(tensor == 100.0)
    
    # x_adv = 100.0 + 10.0 * sign(1.0) = 110.0
    assert torch.all(x_adv == 110.0)
    
    attack.cleanup()
    assert model.zero_grad_called is True


def test_fgsm_zero_gradient() -> None:
    attack = FGSMAttack(FGSMConfig(epsilon=10.0))
    tensor = torch.ones(1, 3, 224, 224, requires_grad=True) * 100.0
    model = MockVictimModel(grad_value=0.0)
    
    attack.validate({"tensor": tensor, "model": model})
    result = attack.execute({})
    
    x_adv = result.artifacts["adversarial_tensor"]
    # x_adv = 100.0 + 10.0 * sign(0.0) = 100.0
    assert torch.all(x_adv == 100.0)


def test_fgsm_clamp_boundaries() -> None:
    attack = FGSMAttack(FGSMConfig(epsilon=200.0, clamp_min=0.0, clamp_max=255.0))
    
    # Positive clamp
    tensor_high = torch.ones(1, 3, 224, 224, requires_grad=True) * 200.0
    model = MockVictimModel(grad_value=1.0)
    attack.validate({"tensor": tensor_high, "model": model})
    res_high = attack.execute({})
    assert torch.all(res_high.artifacts["adversarial_tensor"] == 255.0)
    
    # Negative clamp
    tensor_low = torch.ones(1, 3, 224, 224, requires_grad=True) * 50.0
    model_neg = MockVictimModel(grad_value=-1.0)
    attack.validate({"tensor": tensor_low, "model": model_neg})
    res_low = attack.execute({})
    assert torch.all(res_low.artifacts["adversarial_tensor"] == 0.0)


def test_fgsm_validation_failures() -> None:
    attack = FGSMAttack(FGSMConfig(epsilon=10.0))
    model = MockVictimModel()
    
    with pytest.raises(AttackValidationException, match="Missing 'tensor'"):
        attack.validate({"model": model})
        
    with pytest.raises(AttackValidationException, match="Missing 'model'"):
        attack.validate({"tensor": torch.ones(1, 3, 224, 224)})
        
    with pytest.raises(AttackValidationException, match="at least 3 dimensions"):
        attack.validate({"tensor": torch.ones(224, 224, requires_grad=True), "model": model})
        
        
    with pytest.raises(AttackValidationException, match="must be a PyTorch tensor"):
        attack.validate({"tensor": "string", "model": model})
        
    with pytest.raises(AttackValidationException, match="must implement IVictimModel interface"):
        attack.validate({"tensor": torch.ones(1, 3, 224, 224), "model": "string"})

    with pytest.raises(AttackValidationException, match="Expected 3 channels"):
        attack.validate({"tensor": torch.ones(1, 1, 224, 224), "model": model})
        
    with pytest.raises(AttackValidationException, match="floating point"):
        attack.validate({"tensor": torch.ones(1, 3, 224, 224, dtype=torch.int32), "model": model})
        
    tensor_nan = torch.ones(1, 3, 224, 224)
    tensor_nan[0, 0, 0, 0] = float('nan')
    with pytest.raises(AttackValidationException, match="NaN or Inf"):
        attack.validate({"tensor": tensor_nan, "model": model})
        
    with pytest.raises(AttackValidationException, match="requires_grad must be True"):
        attack.validate({"tensor": torch.ones(1, 3, 224, 224), "model": model})
        
    with pytest.raises(AttackExecutionException, match="Attack not validated properly"):
        attack.execute({})
        
    # Test execution exception propagation
    class ThrowingModel(MockVictimModel):
        def compute_gradients(self, tensor, *args, **kwargs):
            raise AttackExecutionException("Failed inside gradient service")
            
    attack.validate({"tensor": torch.ones(1, 3, 224, 224, requires_grad=True), "model": ThrowingModel()})
    with pytest.raises(AttackExecutionException, match="Failed inside gradient service"):
        attack.execute({})
        
    # Initialization has no side effects but runs successfully
    attack.initialize()
