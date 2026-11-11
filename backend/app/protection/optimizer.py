import torch

class PerturbationOptimizer:
    @staticmethod
    def optimize(original: torch.Tensor, raw_perturbation: torch.Tensor, epsilon: float) -> tuple[torch.Tensor, torch.Tensor]:
        if original.ndim == 3:
            original = original.unsqueeze(0)
            
        clamped_perturbation = torch.clamp(raw_perturbation, -epsilon, epsilon)
        adv = original + clamped_perturbation
        adv = torch.clamp(adv, 0.0, 255.0)
        true_perturbation = adv - original
        
        return adv, true_perturbation
