from typing import Any

from pydantic import BaseModel


class ResponseMetadata(BaseModel):
    request_id: str
    process_time_ms: float | None = None
    error_code: str | None = None
    details: dict[str, Any] | None = None
