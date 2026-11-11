from pydantic import BaseModel

from app.domain.value_objects.image_dimensions import ImageDimensions


class UploadedImageEntity(BaseModel):
    file_id: str
    filename: str
    dimensions: ImageDimensions
    format: str
    mode: str
    size_bytes: int
    path: str
