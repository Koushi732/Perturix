import torch

class PerturbationValidator:
    @staticmethod
    def validate_input(tensor: torch.Tensor) -> None:
        if tensor.ndim < 3 or tensor.ndim > 4:
            raise ValueError("Tensor must be 3D or 4D")
        channels = tensor.shape[1] if tensor.ndim == 4 else tensor.shape[0]
        if channels != 3:
            raise ValueError("Tensor must have 3 channels (RGB)")
        if torch.isnan(tensor).any() or torch.isinf(tensor).any():
            raise ValueError("Tensor contains NaN or Inf")
            
    @staticmethod
    def validate_output(original: torch.Tensor, adv: torch.Tensor, epsilon: float) -> None:
        if original.shape != adv.shape:
            raise ValueError("Shape mismatch between original and adversarial tensor")
        diff = torch.abs(adv - original)
        if (diff > epsilon + 1e-4).any():
            max_diff = diff.max().item()
            raise ValueError(f"Perturbation exceeds L_inf bound of {epsilon}. Max diff: {max_diff}")
