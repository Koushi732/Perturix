class HistoryException(Exception):
    """Base exception for all history module errors."""


class SessionNotFoundException(HistoryException):
    """Raised when a processing session is not found."""


class EvaluationNotFoundException(HistoryException):
    """Raised when an evaluation is not found."""


class AttackNotFoundException(HistoryException):
    """Raised when an attack execution is not found."""
