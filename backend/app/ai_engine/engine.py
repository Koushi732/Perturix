from typing import Any

from app.ai_engine.models import AttackResult
from app.ai_engine.pipeline import PipelineExecutor
from app.ai_engine.registry import IAttackRegistry


class EngineService:
    """Public API for interacting with the AI Engine backend."""
    def __init__(self, registry: IAttackRegistry, pipeline: PipelineExecutor):
        self.registry = registry
        self.pipeline = pipeline
        
    def execute_attack(self, attack_name: str, inputs: dict[str, Any]) -> AttackResult:
        """Executes a registered attack by delegating to the rigid pipeline."""
        return self.pipeline.execute_pipeline(attack_name, inputs)
        
    def get_available_attacks(self) -> list[str]:
        return self.registry.list_attacks()
