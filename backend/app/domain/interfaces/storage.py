from abc import ABC, abstractmethod
from typing import BinaryIO


class IStorageProvider(ABC):
    @abstractmethod
    async def save_file(self, file_id: str, data: BinaryIO) -> str:
        """Saves a file and returns its path or URI."""

    @abstractmethod
    async def get_file(self, file_id: str) -> BinaryIO:
        """Retrieves a file by ID."""

    @abstractmethod
    async def delete_file(self, file_id: str) -> bool:
        """Deletes a file by ID."""
