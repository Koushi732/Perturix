from app.dependencies.ai import get_attack_registry, get_engine_service
from app.dependencies.evaluation import get_evaluation_engine
from app.dependencies.history import get_history_service
from app.services.workflow import AttackWorkflowService

_workflow_service: AttackWorkflowService | None = None


def get_workflow_service() -> AttackWorkflowService:
    global _workflow_service
    if _workflow_service is None:
        _workflow_service = AttackWorkflowService(
            history_service=get_history_service(),
            pipeline=get_engine_service().pipeline,
            attack_registry=get_attack_registry(),
            evaluation_engine=get_evaluation_engine()
        )
    return _workflow_service
