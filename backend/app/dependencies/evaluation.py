from app.evaluation.engine import EvaluationEngine
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
from app.evaluation.registry import MetricRegistry

_global_registry = MetricRegistry()

_global_registry.register(PSNRMetric())
_global_registry.register(SSIMMetric())
_global_registry.register(LPIPSMetric())
_global_registry.register(L0Metric())
_global_registry.register(L2Metric())
_global_registry.register(LinfMetric())
_global_registry.register(RuntimeMetric())
_global_registry.register(ConfidenceMetric())

_global_engine = EvaluationEngine(registry=_global_registry)

def get_evaluation_registry() -> MetricRegistry:
    return _global_registry

def get_evaluation_engine() -> EvaluationEngine:
    return _global_engine
