from typing import Any

import pytest

from app.ai_engine.base import BaseAttack
from app.ai_engine.models import AttackResult
from app.ai_engine.pipeline import PipelineExecutor
from app.ai_engine.registry import AttackRegistry
from app.core.exceptions import (
    AttackExecutionException,
    AttackNotFoundException,
    AttackValidationException,
)


class MockAttack(BaseAttack):
    def __init__(self, name="MockAttack", version="1.0"):
        self._name = name
        self._version = version
        self.cleanup_called = False
    
    @property
    def name(self) -> str:
        return self._name
        
    @property
    def version(self) -> str:
        return self._version

    def initialize(self) -> None:
        pass

    def validate(self, inputs: dict[str, Any]) -> None:
        if "fail_validation" in inputs:
            raise ValueError("Validation specifically failed.")

    def execute(self, inputs: dict[str, Any]) -> AttackResult:
        if "fail_execution" in inputs:
            raise RuntimeError("Execution explicitly failed.")
        return AttackResult(
            attack_name=self.name,
            success=True,
            execution_time_ms=0,
            original_metadata={},
            protected_metadata={},
            artifacts={}
        )

    def cleanup(self) -> None:
        self.cleanup_called = True

def test_registry_registration():
    registry = AttackRegistry()
    attack = MockAttack()
    registry.register(attack)
    assert "mockattack" in registry.list_attacks()
    
    with pytest.raises(ValueError):
        registry.register(attack)  # duplicate

def test_registry_unregistration():
    registry = AttackRegistry()
    attack = MockAttack()
    registry.register(attack)
    registry.unregister("MockAttack")
    assert "MockAttack" not in registry.list_attacks()
    
    with pytest.raises(ValueError):
        registry.unregister("MockAttack")  # duplicate unregister

def test_registry_lookup():
    registry = AttackRegistry()
    attack = MockAttack()
    registry.register(attack)
    assert registry.lookup("MockAttack") == attack
    
    with pytest.raises(AttackNotFoundException):
        registry.lookup("DoesNotExist")
        
def test_pipeline_success():
    registry = AttackRegistry()
    attack = MockAttack()
    registry.register(attack)
    pipeline = PipelineExecutor(registry)
    
    result = pipeline.execute_pipeline("MockAttack", {})
    assert result.success is True
    assert result.attack_name == "MockAttack"
    assert attack.cleanup_called is True

def test_pipeline_validation_failure():
    registry = AttackRegistry()
    attack = MockAttack()
    registry.register(attack)
    pipeline = PipelineExecutor(registry)
    
    with pytest.raises(AttackValidationException):
        pipeline.execute_pipeline("MockAttack", {"fail_validation": True})
        
    assert attack.cleanup_called is False

def test_pipeline_execution_failure():
    registry = AttackRegistry()
    attack = MockAttack()
    registry.register(attack)
    pipeline = PipelineExecutor(registry)
    
    with pytest.raises(AttackExecutionException):
        pipeline.execute_pipeline("MockAttack", {"fail_execution": True})
        
    assert attack.cleanup_called is True
