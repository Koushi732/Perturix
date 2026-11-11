from typing import Protocol

from app.ai_engine.base import BaseAttack
from app.core.exceptions import AttackNotFoundException


class IAttackRegistry(Protocol):
    def register(self, attack: BaseAttack) -> None: ...
    def unregister(self, attack_name: str) -> None: ...
    def lookup(self, attack_name: str) -> BaseAttack: ...
    def list_attacks(self) -> list[str]: ...


class AttackRegistry(IAttackRegistry):
    def __init__(self) -> None:
        self._attacks: dict[str, BaseAttack] = {}

    def register(self, attack: BaseAttack) -> None:
        """Registers a new attack plugin."""
        name_lower = attack.name.lower()
        if name_lower in self._attacks:
            raise ValueError(f"Attack '{attack.name}' is already registered.")
        self._attacks[name_lower] = attack

    def unregister(self, attack_name: str) -> None:
        """Unregisters an attack plugin."""
        name_lower = attack_name.lower()
        if name_lower not in self._attacks:
            raise ValueError(f"Cannot unregister. Attack '{attack_name}' not found.")
        del self._attacks[name_lower]

    def lookup(self, attack_name: str) -> BaseAttack:
        """Looks up an attack plugin by name."""
        name_lower = attack_name.lower()
        if name_lower not in self._attacks:
            raise AttackNotFoundException(attack_name)
        return self._attacks[name_lower]

    def list_attacks(self) -> list[str]:
        """Returns a list of all registered attack names."""
        return list(self._attacks.keys())
