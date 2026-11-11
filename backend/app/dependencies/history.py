from app.history.repository import (
    AttackRepository,
    EvaluationRepository,
    ProcessingSessionRepository,
)
from app.history.service import HistoryService

_session_repo = ProcessingSessionRepository()
_attack_repo = AttackRepository()
_eval_repo = EvaluationRepository()
_history_service = HistoryService(_session_repo, _attack_repo, _eval_repo)


def get_processing_repository() -> ProcessingSessionRepository:
    return _session_repo


def get_attack_repository() -> AttackRepository:
    return _attack_repo


def get_evaluation_repository() -> EvaluationRepository:
    return _eval_repo


def get_history_service() -> HistoryService:
    return _history_service
