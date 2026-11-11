from typing import Any, Generic, TypeVar

from pydantic import BaseModel

DataT = TypeVar("DataT")

class StandardResponse(BaseModel, Generic[DataT]):
    success: bool
    message: str
    data: DataT | None = None
    metadata: dict[str, Any] | None = None
    timestamp: str
    request_id: str
