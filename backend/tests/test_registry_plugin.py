import pytest

from app.ai_engine.algorithms.fgsm import FGSMAttack
from app.ai_engine.registry import AttackRegistry


def test_fgsm_registration_resolution() -> None:
    registry = AttackRegistry()
    attack = FGSMAttack()
    
    registry.register(attack)
    
    resolved_attack = registry.lookup("FGSM")
    assert resolved_attack is attack


def test_fgsm_registration_metadata() -> None:
    registry = AttackRegistry()
    attack = FGSMAttack()
    
    registry.register(attack)
    
    metadata = registry.list_attacks()
    assert "fgsm" in metadata


def test_fgsm_duplicate_registration_rejected() -> None:
    registry = AttackRegistry()
    attack = FGSMAttack()
    
    registry.register(attack)
    
    with pytest.raises(ValueError, match="already registered"):
        registry.register(attack)
