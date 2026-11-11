from app.ai_engine.algorithms.fgsm import FGSMAttack
from app.ai_engine.engine import EngineService
from app.ai_engine.pipeline import PipelineExecutor
from app.ai_engine.registry import AttackRegistry

# Application-level ownership (instantiated once, but it's a standard class)
_global_registry = AttackRegistry()
_global_registry.register(FGSMAttack())
_global_engine = EngineService(_global_registry, PipelineExecutor(_global_registry))

def get_attack_registry() -> AttackRegistry:
    return _global_registry

def get_engine_service() -> EngineService:
    return _global_engine
