import pytest

from app.evaluation.base import BaseMetric
from app.evaluation.context import EvaluationContext
from app.evaluation.registry import MetricRegistry


class MockMetric(BaseMetric):
    @property
    def name(self) -> str:
        return "Mock"
        
    @property
    def version(self) -> str:
        return "1.0.0"
        
    def compute(self, context: EvaluationContext) -> float:
        return 1.0


def test_registry_register_lookup() -> None:
    reg = MetricRegistry()
    m = MockMetric()
    reg.register(m)
    assert reg.lookup("Mock") is m


def test_registry_duplicate() -> None:
    reg = MetricRegistry()
    m = MockMetric()
    reg.register(m)
    with pytest.raises(ValueError, match="already registered"):
        reg.register(m)


def test_registry_unregister() -> None:
    reg = MetricRegistry()
    m = MockMetric()
    reg.register(m)
    reg.unregister("Mock")
    with pytest.raises(ValueError, match="not found"):
        reg.lookup("Mock")


def test_registry_list() -> None:
    reg = MetricRegistry()
    m = MockMetric()
    reg.register(m)
    lst = reg.list_metrics()
    assert len(lst) == 1
    assert lst[0]["name"] == "Mock"
    assert lst[0]["version"] == "1.0.0"


def test_registry_get_all() -> None:
    reg = MetricRegistry()
    m = MockMetric()
    reg.register(m)
    assert len(reg.get_all()) == 1
    assert reg.get_all()[0] is m
