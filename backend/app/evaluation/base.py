from abc import ABC, abstractmethod
from typing import Any

from .context import EvaluationContext


class BaseMetric(ABC):
    """
    Abstract base class for all evaluation metrics.
    Follows the lifecycle: initialize -> validate -> compute -> cleanup.
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """The distinct name of the metric (e.g., 'PSNR', 'L2')."""
        
    @property
    @abstractmethod
    def version(self) -> str:
        """The version string (e.g., '1.0.0')."""

    def initialize(self) -> None:
        """Optional initialization logic."""

    def validate(self, context: EvaluationContext) -> None:
        """
        Validates the inputs required for this metric.
        Raises MetricValidationException on failure.
        """

    @abstractmethod
    def compute(self, context: EvaluationContext) -> float | bool | dict[str, Any] | None:
        """
        Computes the metric from the context.
        Raises MetricExecutionException on failure.
        """

    def cleanup(self) -> None:
        """Optional cleanup logic."""
