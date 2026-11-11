
from pydantic import BaseModel


class PreprocessingConfig(BaseModel):
    """Configuration options for image preprocessing."""
    target_size: tuple[int, int] | None = None
    normalize: bool = True
    add_batch_dimension: bool = True
    to_rgb: bool = True
