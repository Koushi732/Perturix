import os
from typing import BinaryIO

import aiofiles

from app.config.settings import settings
from app.domain.interfaces.storage import IStorageProvider


class LocalStorageProvider(IStorageProvider):
    def __init__(self, upload_dir: str = str(settings.upload_dir)):
        self.upload_dir = os.path.abspath(upload_dir)
        
        if not os.path.exists(self.upload_dir):
            os.makedirs(self.upload_dir, exist_ok=True)

    def _get_safe_path(self, filename: str) -> str:
        """Resolves the path and prevents path traversal attacks."""
        safe_path = os.path.abspath(os.path.join(self.upload_dir, filename))
        if not safe_path.startswith(self.upload_dir):
            raise ValueError("Path traversal attempt detected.")
        return safe_path

    async def save_file(self, file_id: str, data: BinaryIO) -> str:
        # Expected `data` to actually be an `UploadFile` for aiofiles streams
        # But per interface it's BinaryIO. If it's a FastAPI UploadFile, we can read chunks.
        # For simplicity and adhering to IStorageProvider:
        safe_path = self._get_safe_path(file_id)
        
        # Atomic write by writing to a .tmp file then renaming
        tmp_path = safe_path + ".tmp"
        try:
            async with aiofiles.open(tmp_path, "wb") as f:
                if hasattr(data, 'read'):
                    # if it is an async upload file
                    if hasattr(data, 'read') and callable(data.read) and not hasattr(data, '_file'):
                        # synchronous fallback
                        while True:
                            chunk = data.read(1024 * 1024)
                            if not chunk:
                                break
                            await f.write(chunk)
                    else:
                        # FastAPI UploadFile async read
                        while True:
                            chunk = await data.read(1024 * 1024)  # type: ignore[misc]
                            if not chunk:
                                break
                            await f.write(chunk)
                else:
                    await f.write(data) # type: ignore

            os.replace(tmp_path, safe_path)
            return safe_path
        except Exception:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
            raise

    async def get_file(self, file_id: str) -> BinaryIO:
        safe_path = self._get_safe_path(file_id)
        if not os.path.exists(safe_path):
            raise FileNotFoundError(f"File {file_id} not found.")
        return open(safe_path, "rb")  # noqa: ASYNC230 (interface requires synchronous BinaryIO)

    async def delete_file(self, file_id: str) -> bool:
        safe_path = self._get_safe_path(file_id)
        if os.path.exists(safe_path):
            os.remove(safe_path)
            return True
        return False
