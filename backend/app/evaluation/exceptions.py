class EvaluationException(Exception):
    """Base exception for all evaluation-related errors."""


class MetricValidationException(EvaluationException):
    """Raised when a metric's validation fails (e.g., shape mismatch, NaN)."""


class MetricExecutionException(EvaluationException):
    """Raised when a metric fails to compute or raises an internal error."""
