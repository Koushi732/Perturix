import logging

import numpy as np
import torch
from PIL import Image

logger = logging.getLogger(__name__)

def load_image(filepath: str) -> Image.Image:
    """Loads an image from disk."""
    logger.info(f"Loading image from {filepath}")
    return Image.open(filepath)

def convert_to_rgb(image: Image.Image) -> Image.Image:
    """Converts image to RGB, removing alpha channel if present."""
    if image.mode != "RGB":
        logger.info(f"Converting image from {image.mode} to RGB")
        return image.convert("RGB")
    return image

def resize_image(image: Image.Image, target_size: tuple[int, int]) -> Image.Image:
    """Resizes image to target dimensions."""
    logger.info(f"Resizing image to {target_size}")
    return image.resize(target_size, Image.Resampling.BILINEAR)

def image_to_numpy(image: Image.Image) -> np.ndarray:
    """Converts a Pillow image to a NumPy array."""
    return np.array(image)

def numpy_to_tensor(array: np.ndarray) -> torch.Tensor:
    """Converts a NumPy array to a PyTorch tensor and reshapes to (C, H, W)."""
    logger.info("Converting NumPy array to PyTorch tensor")
    # Image array shape is (H, W, C). We need to transpose to (C, H, W).
    tensor = torch.from_numpy(array).float()
    if tensor.ndim == 3:
        tensor = tensor.permute(2, 0, 1)
    return tensor

def normalize_tensor(tensor: torch.Tensor) -> torch.Tensor:
    """Normalizes tensor pixel values from [0, 255] to [0.0, 1.0]."""
    logger.info("Normalizing tensor to [0, 1]")
    return tensor / 255.0

def prepare_batch(tensor: torch.Tensor) -> torch.Tensor:
    """Adds a batch dimension resulting in shape (1, C, H, W)."""
    logger.info("Adding batch dimension")
    return tensor.unsqueeze(0)
