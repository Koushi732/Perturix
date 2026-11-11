import pytest
import torch

from app.evaluation.context import EvaluationContext
from app.evaluation.exceptions import (
    MetricValidationException,
)
from app.evaluation.metrics import (
    ConfidenceMetric,
    L0Metric,
    L2Metric,
    LinfMetric,
    LPIPSMetric,
    PSNRMetric,
    RuntimeMetric,
    SSIMMetric,
)


def test_validation_mismatched_shapes() -> None:
    ctx = EvaluationContext(
        original_tensor=torch.ones(1, 3, 224, 224),
        adversarial_tensor=torch.ones(1, 3, 224, 225)
    )
    m = L0Metric()
    with pytest.raises(MetricValidationException, match="shapes must match"):
        m.validate(ctx)


def test_validation_nan() -> None:
    orig = torch.ones(1, 3, 224, 224)
    orig[0, 0, 0, 0] = float('nan')
    ctx = EvaluationContext(
        original_tensor=orig,
        adversarial_tensor=torch.ones(1, 3, 224, 224)
    )
    m = L0Metric()
    with pytest.raises(MetricValidationException, match="NaN"):
        m.validate(ctx)


def test_validation_inf() -> None:
    ctx = EvaluationContext(
        original_tensor=torch.ones(1, 3, 224, 224),
        adversarial_tensor=torch.ones(1, 3, 224, 224) * float('inf')
    )
    m = L0Metric()
    with pytest.raises(MetricValidationException, match="Inf"):
        m.validate(ctx)
        
        
def test_validation_invalid_images() -> None:
    ctx = EvaluationContext(
        original_tensor=torch.ones(1, 2, 224, 224),
        adversarial_tensor=torch.ones(1, 2, 224, 224)
    )
    m = L0Metric()
    with pytest.raises(MetricValidationException, match="3 channels"):
        m.validate(ctx)


def test_l0_metric() -> None:
    orig = torch.ones(1, 3, 2, 2)
    adv = torch.ones(1, 3, 2, 2)
    adv[0, 0, 0, 0] = 2.0
    ctx = EvaluationContext(original_tensor=orig, adversarial_tensor=adv)
    m = L0Metric()
    assert m.compute(ctx) == 1.0


def test_l2_metric() -> None:
    orig = torch.ones(1, 3, 2, 2)
    adv = torch.ones(1, 3, 2, 2)
    adv[0, 0, 0, 0] = 4.0 # diff is 3.0, L2 is sqrt(9) = 3.0
    ctx = EvaluationContext(original_tensor=orig, adversarial_tensor=adv)
    m = L2Metric()
    assert m.compute(ctx) == 3.0


def test_linf_metric() -> None:
    orig = torch.ones(1, 3, 2, 2)
    adv = torch.ones(1, 3, 2, 2)
    adv[0, 0, 0, 0] = 5.0 # diff is 4.0
    adv[0, 1, 0, 0] = 2.0 # diff is 1.0
    ctx = EvaluationContext(original_tensor=orig, adversarial_tensor=adv)
    m = LinfMetric()
    assert m.compute(ctx) == 4.0


def test_runtime_metric() -> None:
    ctx = EvaluationContext(
        original_tensor=torch.ones(1, 3, 224, 224),
        adversarial_tensor=torch.ones(1, 3, 224, 224),
        attack_execution_time_ms=123.4
    )
    m = RuntimeMetric()
    assert m.compute(ctx) == 123.4
    
    ctx2 = EvaluationContext(
        original_tensor=torch.ones(1), adversarial_tensor=torch.ones(1)
    )
    with pytest.raises(MetricValidationException):
        m.validate(ctx2)


def test_confidence_metric() -> None:
    orig_probs = torch.tensor([[0.1, 0.8, 0.1]])
    adv_probs = torch.tensor([[0.6, 0.3, 0.1]])
    ctx = EvaluationContext(
        original_tensor=torch.ones(1),
        adversarial_tensor=torch.ones(1),
        original_probabilities=orig_probs,
        adversarial_probabilities=adv_probs
    )
    m = ConfidenceMetric()
    res = m.compute(ctx)
    assert isinstance(res, dict)
    assert res["confidence_before"] == pytest.approx(0.8)
    assert res["confidence_after"] == pytest.approx(0.3)
    assert res["confidence_drop"] == pytest.approx(0.5)
    assert res["attack_success"] is True

    # Test validation failures
    orig_probs_nan = orig_probs.clone()
    orig_probs_nan[0, 0] = float('nan')
    ctx2 = EvaluationContext(
        original_tensor=torch.ones(1), adversarial_tensor=torch.ones(1),
        original_probabilities=orig_probs_nan, adversarial_probabilities=adv_probs
    )
    with pytest.raises(MetricValidationException, match="NaN"):
        m.validate(ctx2)


def test_psnr_metric() -> None:
    orig = torch.ones(1, 3, 224, 224) * 100.0
    adv = torch.ones(1, 3, 224, 224) * 110.0
    ctx = EvaluationContext(original_tensor=orig, adversarial_tensor=adv)
    m = PSNRMetric()
    m.initialize()
    res = m.compute(ctx)
    assert isinstance(res, float)
    m.cleanup()


def test_ssim_metric() -> None:
    orig = torch.ones(1, 3, 224, 224) * 100.0
    adv = torch.ones(1, 3, 224, 224) * 110.0
    ctx = EvaluationContext(original_tensor=orig, adversarial_tensor=adv)
    m = SSIMMetric()
    m.initialize()
    res = m.compute(ctx)
    assert isinstance(res, float)
    m.cleanup()


def test_lpips_metric() -> None:
    orig = torch.ones(1, 3, 224, 224) * 100.0
    adv = torch.ones(1, 3, 224, 224) * 110.0
    ctx = EvaluationContext(original_tensor=orig, adversarial_tensor=adv)
    m = LPIPSMetric()
    m.initialize()
    res = m.compute(ctx)
    assert isinstance(res, float)
    m.cleanup()
