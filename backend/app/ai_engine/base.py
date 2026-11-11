from abc import ABC, abstractmethod
from typing import Any

from app.ai_engine.models import AttackResult


class BaseAttack(ABC):
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Returns the name of the attack."""
        
    @property
    @abstractmethod
    def version(self) -> str:
        """Returns the version of the attack."""

    @abstractmethod
    def initialize(self) -> None:
        """Initialize the attack parameters and models."""

    @abstractmethod
    def validate(self, inputs: dict[str, Any]) -> None:
        """Validates the input parameters for the attack."""

    @abstractmethod
    def execute(self, inputs: dict[str, Any]) -> AttackResult:
        """Executes the perturbation algorithm."""

    @abstractmethod
    def cleanup(self) -> None:
        """Cleans up memory and resources."""
