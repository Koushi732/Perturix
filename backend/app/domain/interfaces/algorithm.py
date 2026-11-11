from abc import ABC, abstractmethod
from typing import Any


class IAlgorithm(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        """Returns the name of the algorithm."""
        
    @abstractmethod
    async def protect(self, tensor: Any, epsilon: float) -> Any:
        """Applies the perturbation and returns the protected tensor."""
