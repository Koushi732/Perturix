
from pydantic import BaseModel

from app.schemas.common.metadata import ResponseMetadata


class ErrorResponse(BaseModel):
    success: bool = False
    message: str
    data: dict | None = None
    metadata: ResponseMetadata
    timestamp: str
