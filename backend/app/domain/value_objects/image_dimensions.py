from pydantic import BaseModel


class ImageDimensions(BaseModel):
    width: int
    height: int
