import torch
from .models import VerificationStats

class PerturbationAnalyzer:
    @staticmethod
    def analyze(perturbation: torch.Tensor, epsilon: float) -> VerificationStats:
        p = perturbation.squeeze(0) if perturbation.ndim == 4 else perturbation
        abs_p = torch.abs(p)
        max_p_per_pixel, _ = torch.max(abs_p, dim=0)
        
        coverage_mask = max_p_per_pixel > 1e-5
        coverage = coverage_mask.float().mean().item()
        
        strength = (abs_p.mean().item() / epsilon) if epsilon > 0 else 0.0
        strength = min(1.0, strength * 2.0)
        
        density_mask = max_p_per_pixel > (epsilon * 0.95)
        density = density_mask.float().mean().item()
        
        entropy = min(1.0, float(torch.std(p).item()) / (epsilon / 2) if epsilon > 0 else 0)
        
        diff_y = torch.abs(p[:, 1:, :] - p[:, :-1, :]).mean().item()
        diff_x = torch.abs(p[:, :, 1:] - p[:, :, :-1]).mean().item()
        grad_consistency = min(1.0, ((diff_y + diff_x) / 2) / epsilon if epsilon > 0 else 0)
        
        score = (0.25 * coverage) + (0.25 * strength) + (0.20 * entropy) + (0.15 * density) + (0.15 * grad_consistency)
        verification_score = min(100.0, max(0.0, score * 100))
        
        return VerificationStats(
            coverage=coverage,
            strength=strength,
            entropy=entropy,
            density=density,
            gradient_consistency=grad_consistency,
            verification_score=verification_score,
            status="VALID" if verification_score > 30 else "WEAK"
        )
