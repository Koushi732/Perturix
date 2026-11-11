import numpy as np
import torch
from PIL import Image


class TensorValidationError(ValueError):
    pass

def validate_tensor(tensor: torch.Tensor) -> None:
    """Rigorous constraints for Perturix Tensors."""
    if tensor.dtype != torch.float32:
        raise TensorValidationError(f"Expected dtype float32, got {tensor.dtype}")
    
    if tensor.dim() != 3:
        raise TensorValidationError(f"Expected 3D tensor (C, H, W), got {tensor.dim()}D shape {tensor.shape}")
        
    if tensor.shape[0] != 3:
        raise TensorValidationError(f"Expected 3 channels (RGB), got {tensor.shape[0]}")
        
    if not torch.isfinite(tensor).all():
        raise TensorValidationError("Tensor contains NaN or Infinite values.")

def pil_to_numpy(image: Image.Image) -> np.ndarray:
    """
    Convert PIL image to numpy array, strictly enforcing RGB.
    
    Contract:
    Tensor utilities are raw conversion utilities.
    They perform PIL -> NumPy -> Tensor without:
    - normalization
    - standardization
    - preprocessing
    - resizing
    - channel manipulation
    
    The returned numpy array is strictly in the raw [0, 255] range.
    """
    if image.mode != "RGB":
        image = image.convert("RGB")
    return np.array(image, dtype=np.float32)

def numpy_to_pil(array: np.ndarray) -> Image.Image:
    """
    Convert numpy array (H, W, C) back to PIL Image.
    
    Contract:
    Expected input array values are raw [0, 255].
    Clips values to [0, 255] securely to avoid under/overflow 
    but does NOT perform denormalization.
    """
    if np.isnan(array).any() or np.isinf(array).any():
        raise TensorValidationError("Numpy array contains NaN or Infinite values.")
        
    # Clip to [0, 255] range to avoid under/overflow
    array = np.clip(array, 0.0, 255.0)
    array = array.astype(np.uint8)
    return Image.fromarray(array, mode="RGB")

def pil_to_tensor(image: Image.Image) -> torch.Tensor:
    """Convert PIL Image strictly into a validated [C, H, W] Torch Tensor."""
    # Convert PIL to Numpy [H, W, C]
    np_array = pil_to_numpy(image)
    # Convert to Tensor [C, H, W]
    tensor = torch.from_numpy(np_array).permute(2, 0, 1)
    validate_tensor(tensor)
    return tensor

def tensor_to_pil(tensor: torch.Tensor) -> Image.Image:
    """Convert Torch Tensor [C, H, W] securely back into a PIL Image."""
    validate_tensor(tensor)
    # Permute back to [H, W, C]
    tensor_hwc = tensor.permute(1, 2, 0).detach().cpu()
    return numpy_to_pil(tensor_hwc.numpy())
