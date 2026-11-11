import pytest
import torch
import numpy as np

from app.protection.validator import PerturbationValidator
from app.protection.optimizer import PerturbationOptimizer
from app.protection.analyzer import PerturbationAnalyzer
from app.protection.models import VerificationStats

def test_validator_input():
    # Valid
    valid_tensor = torch.rand(1, 3, 224, 224)
    PerturbationValidator.validate_input(valid_tensor)
    
    # Invalid channels
    with pytest.raises(ValueError, match="3 channels"):
        PerturbationValidator.validate_input(torch.rand(1, 4, 224, 224))
        
    # Invalid dims
    with pytest.raises(ValueError, match="3D or 4D"):
        PerturbationValidator.validate_input(torch.rand(3, 224))
        
    # NaN
    nan_tensor = torch.rand(1, 3, 224, 224)
    nan_tensor[0, 0, 0, 0] = float("nan")
    with pytest.raises(ValueError, match="NaN or Inf"):
        PerturbationValidator.validate_input(nan_tensor)

def test_optimizer_clipping():
    original = torch.zeros(1, 3, 10, 10)
    raw_perturbation = torch.ones(1, 3, 10, 10) * 0.1  # 10% change
    
    # Epsilon is 0.05
    adv, true_p = PerturbationOptimizer.optimize(original, raw_perturbation, 0.05)
    
    # The max perturbation should be bounded by epsilon
    assert torch.max(true_p).item() == pytest.approx(0.05)
    assert torch.max(adv).item() == pytest.approx(0.05)
    
    # Check RGB bounds
    original = torch.ones(1, 3, 10, 10) * 250.0
    raw_perturbation = torch.ones(1, 3, 10, 10) * 10.0
    adv, true_p = PerturbationOptimizer.optimize(original, raw_perturbation, 10.0)
    
    # It should clip to 255.0 (RGB max)
    assert torch.max(adv).item() == pytest.approx(255.0)
    # The actual perturbation applied will be only 5.0
    assert torch.max(true_p).item() == pytest.approx(5.0)

def test_analyzer_stats():
    # Construct a dummy perturbation where exactly half the pixels are changed by epsilon
    perturbation = torch.zeros(1, 3, 10, 10)
    epsilon = 0.1
    perturbation[:, :, :5, :] = epsilon
    
    stats = PerturbationAnalyzer.analyze(perturbation, epsilon)
    
    assert isinstance(stats, VerificationStats)
    # Half the pixels changed
    assert stats.coverage == pytest.approx(0.5)
    # Average magnitude is epsilon/2 across the image
    assert stats.strength == pytest.approx(1.0) # scaled
    
    assert stats.verification_score > 0
    assert stats.status == "VALID"
