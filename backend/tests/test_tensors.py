import numpy as np
import pytest
import torch
from PIL import Image

from app.services.image.tensor import (
    TensorValidationError,
    pil_to_tensor,
    tensor_to_pil,
    validate_tensor,
)


def test_tensor_validation():
    # Valid
    valid_tensor = torch.rand(3, 100, 100, dtype=torch.float32)
    validate_tensor(valid_tensor)
    
    # Invalid dtype
    with pytest.raises(TensorValidationError):
        validate_tensor(torch.rand(3, 100, 100, dtype=torch.float64))
        
    # Invalid shape
    with pytest.raises(TensorValidationError):
        validate_tensor(torch.rand(100, 100, dtype=torch.float32))
        
    # Invalid channel count (RGBA)
    with pytest.raises(TensorValidationError):
        validate_tensor(torch.rand(4, 100, 100, dtype=torch.float32))
        
    # NaN values
    nan_tensor = torch.rand(3, 100, 100, dtype=torch.float32)
    nan_tensor[0, 0, 0] = float('nan')
    with pytest.raises(TensorValidationError):
        validate_tensor(nan_tensor)

    # Inf values
    inf_tensor = torch.rand(3, 100, 100, dtype=torch.float32)
    inf_tensor[0, 0, 0] = float('inf')
    with pytest.raises(TensorValidationError):
        validate_tensor(inf_tensor)

def test_grayscale_to_tensor():
    # Grayscale image converts to RGB under the hood
    gray = Image.new("L", (100, 100), color=128)
    tensor = pil_to_tensor(gray)
    assert tensor.shape == (3, 100, 100)
    
def test_rgba_to_tensor():
    rgba = Image.new("RGBA", (100, 100), color=(255, 0, 0, 128))
    tensor = pil_to_tensor(rgba)
    assert tensor.shape == (3, 100, 100)
    
def test_tensor_to_pil_roundtrip():
    original = Image.new("RGB", (100, 100), color=(255, 128, 0))
    tensor = pil_to_tensor(original)
    reconstructed = tensor_to_pil(tensor)
    
    # Exact pixel match checking
    orig_np = np.array(original)
    recon_np = np.array(reconstructed)
    assert np.allclose(orig_np, recon_np)
