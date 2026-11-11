
import torch

from app.evaluation.base import BaseMetric
from app.evaluation.context import EvaluationContext
from app.evaluation.engine import EvaluationEngine
from app.evaluation.exceptions import MetricExecutionException
from app.evaluation.registry import MetricRegistry


class MockMetricSuccess(BaseMetric):
    @property
    def name(self) -> str: return "SuccessMetric"
    @property
    def version(self) -> str: return "1.0"
    def compute(self, context: EvaluationContext) -> float: return 42.0


class MockMetricFailure(BaseMetric):
    @property
    def name(self) -> str: return "FailMetric"
    @property
    def version(self) -> str: return "1.0"
    def compute(self, context: EvaluationContext) -> float: raise MetricExecutionException("Boom")


class MockDictMetric(BaseMetric):
    @property
    def name(self) -> str: return "L0"
    @property
    def version(self) -> str: return "1.0"
    def compute(self, context: EvaluationContext) -> float: return 10.0


def test_engine_orchestration() -> None:
    reg = MetricRegistry()
    reg.register(MockMetricSuccess())
    reg.register(MockMetricFailure())
    reg.register(MockDictMetric())
    
    engine = EvaluationEngine(reg)
    ctx = EvaluationContext(
        original_tensor=torch.zeros(1),
        adversarial_tensor=torch.zeros(1),
        attack_execution_time_ms=100.0,
        attack_memory_usage_mb=50.0
    )
    
    res = engine.evaluate(ctx, "TestAttack", "1.0", "img.png")
    
    # Engine tracks stats
    assert res.execution_time_ms == 100.0
    assert res.memory_usage_mb == 50.0
    
    # Dict Metric unpacked to L0 (since it maps to model field 'l0')
    assert res.l0 == 10.0
    
    # SuccessMetric saved to notes (since SuccessMetric is not a model field)
    assert any("SuccessMetric: 42.0" in n for n in res.notes)
    
    # FailMetric failed without stopping execution
    assert any("FailMetric failed: Boom" in w for w in res.warnings)
    
    assert res.metric_versions["SuccessMetric"] == "1.0"
