import logging
from typing import Any

from .base import BaseMetric

logger = logging.getLogger(__name__)


class MetricRegistry:
    def __init__(self) -> None:
        self._metrics: dict[str, BaseMetric] = {}

    def register(self, metric: BaseMetric) -> None:
        if metric.name in self._metrics:
            raise ValueError(f"Metric '{metric.name}' is already registered.")
        self._metrics[metric.name] = metric
        logger.info(f"Registered evaluation metric: {metric.name} v{metric.version}")

    def unregister(self, name: str) -> None:
        if name in self._metrics:
            del self._metrics[name]
            logger.info(f"Unregistered evaluation metric: {name}")

    def lookup(self, name: str) -> BaseMetric:
        if name not in self._metrics:
            raise ValueError(f"Metric '{name}' not found in registry.")
        return self._metrics[name]

    def list_metrics(self) -> list[dict[str, Any]]:
        return [{"name": name, "version": metric.version} for name, metric in self._metrics.items()]
    
    def get_all(self) -> list[BaseMetric]:
        return list(self._metrics.values())
