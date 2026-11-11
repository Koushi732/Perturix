import os

base_dir = "app/protection"
os.makedirs(base_dir, exist_ok=True)

with open(f"{base_dir}/__init__.py", "w") as f:
    f.write("")

files = {
    "models.py": """from pydantic import BaseModel, ConfigDict
from typing import Any
import torch

class VerificationStats(BaseModel):
    coverage: float
    strength: float
    entropy: float
    density: float
    gradient_consistency: float
    verification_score: float
    status: str

class PerturbationResult(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    adversarial_tensor: torch.Tensor
    perturbation_tensor: torch.Tensor
    verification: VerificationStats
    heatmap_filename: str | None = None
    difference_filename: str | None = None
    overlay_filename: str | None = None
    perturbation_filename: str | None = None
""",
    
    "validator.py": """import torch

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
            raise ValueError(f"Perturbation exceeds L_inf bound of {epsilon}")
""",

    "generator.py": """import torch
from app.ai_engine.pipeline import PipelineExecutor

class PerturbationGenerator:
    def __init__(self, pipeline: PipelineExecutor):
        self.pipeline = pipeline
        
    def generate(self, attack_name: str, inputs: dict) -> torch.Tensor:
        result = self.pipeline.execute_pipeline(attack_name, inputs)
        adv_tensor = result.artifacts["adversarial_tensor"]
        original = inputs["tensor"]
        
        if adv_tensor.ndim == 3:
            adv_tensor = adv_tensor.unsqueeze(0)
        if original.ndim == 3:
            original = original.unsqueeze(0)
            
        perturbation = adv_tensor - original
        return perturbation
""",

    "optimizer.py": """import torch

class PerturbationOptimizer:
    @staticmethod
    def optimize(original: torch.Tensor, raw_perturbation: torch.Tensor, epsilon: float) -> tuple[torch.Tensor, torch.Tensor]:
        if original.ndim == 3:
            original = original.unsqueeze(0)
            
        clamped_perturbation = torch.clamp(raw_perturbation, -epsilon, epsilon)
        adv = original + clamped_perturbation
        adv = torch.clamp(adv, 0.0, 1.0)
        true_perturbation = adv - original
        
        return adv, true_perturbation
""",

    "analyzer.py": """import torch
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
""",

    "visualizer.py": """import torch
import numpy as np
import cv2
from PIL import Image

class PerturbationVisualizer:
    @staticmethod
    def tensor_to_cv2(t: torch.Tensor) -> np.ndarray:
        arr = t.squeeze(0).permute(1, 2, 0).cpu().numpy() if t.ndim == 4 else t.permute(1, 2, 0).cpu().numpy()
        arr = np.clip(arr * 255, 0, 255).astype(np.uint8)
        return cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)
        
    @staticmethod
    def generate_heatmap(perturbation: torch.Tensor, epsilon: float) -> Image.Image:
        p = perturbation.squeeze(0).permute(1, 2, 0).cpu().numpy() if perturbation.ndim == 4 else perturbation.permute(1, 2, 0).cpu().numpy()
        p_mag = np.linalg.norm(p, axis=2)
        p_norm = np.clip(p_mag / (epsilon * np.sqrt(3)), 0, 1)
        p_uint = (p_norm * 255).astype(np.uint8)
        heatmap_bgr = cv2.applyColorMap(p_uint, cv2.COLORMAP_TURBO)
        heatmap_rgb = cv2.cvtColor(heatmap_bgr, cv2.COLOR_BGR2RGB)
        return Image.fromarray(heatmap_rgb)
        
    @staticmethod
    def generate_difference(original: torch.Tensor, adv: torch.Tensor) -> Image.Image:
        orig = PerturbationVisualizer.tensor_to_cv2(original)
        adv_cv2 = PerturbationVisualizer.tensor_to_cv2(adv)
        diff = cv2.absdiff(orig, adv_cv2)
        # Enhance difference visibility for human eyes
        diff = cv2.convertScaleAbs(diff, alpha=10.0, beta=0)
        diff_rgb = cv2.cvtColor(diff, cv2.COLOR_BGR2RGB)
        return Image.fromarray(diff_rgb)
        
    @staticmethod
    def generate_overlay(original: torch.Tensor, heatmap_img: Image.Image) -> Image.Image:
        orig_img = Image.fromarray(cv2.cvtColor(PerturbationVisualizer.tensor_to_cv2(original), cv2.COLOR_BGR2RGB))
        orig_img = orig_img.convert("RGBA")
        heat_img = heatmap_img.convert("RGBA")
        overlay = Image.blend(orig_img, heat_img, alpha=0.5)
        return overlay.convert("RGB")
""",

    "storage.py": """import os
import json
import torch
import numpy as np
from PIL import Image
from app.dependencies.storage import get_storage_provider

class PerturbationStorage:
    def __init__(self):
        self.storage = get_storage_provider()
        self.base_dir = getattr(self.storage, "upload_dir", "uploads")
        
    async def save_artifacts(self, session_id: str, perturbation: torch.Tensor, 
                             heatmap: Image.Image, difference: Image.Image, 
                             overlay: Image.Image, metadata: dict) -> dict:
        import io
        
        def save_pil(img: Image.Image, suffix: str):
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            buf.seek(0)
            filename = f"{session_id}_{suffix}.png"
            # Using synchronous write for simplicity in backend logic, but async storage exists
            with open(os.path.join(self.base_dir, filename), "wb") as f:
                f.write(buf.read())
            return filename
            
        heat_name = save_pil(heatmap, "heatmap")
        diff_name = save_pil(difference, "difference")
        over_name = save_pil(overlay, "overlay")
        
        npy_name = f"{session_id}_perturbation.npy"
        np.save(os.path.join(self.base_dir, npy_name), perturbation.cpu().numpy())
        
        json_name = f"{session_id}_perturbation.json"
        with open(os.path.join(self.base_dir, json_name), "w") as f:
            json.dump(metadata, f, indent=4)
            
        return {
            "heatmap": heat_name,
            "difference": diff_name,
            "overlay": over_name,
            "npy": npy_name,
            "json": json_name
        }
""",

    "engine.py": """import torch
from .models import PerturbationResult
from .validator import PerturbationValidator
from .generator import PerturbationGenerator
from .optimizer import PerturbationOptimizer
from .analyzer import PerturbationAnalyzer
from .visualizer import PerturbationVisualizer
from .storage import PerturbationStorage
from app.ai_engine.pipeline import PipelineExecutor
from datetime import UTC, datetime

class ProtectionEngine:
    version = "2.0"
    
    def __init__(self, pipeline: PipelineExecutor):
        self.generator = PerturbationGenerator(pipeline)
        self.storage = PerturbationStorage()
        
    async def process(self, attack_name: str, inputs: dict, epsilon: float, save_research_artifacts: bool, session_id: str) -> PerturbationResult:
        original = inputs["tensor"]
        
        PerturbationValidator.validate_input(original)
        
        raw_perturbation = self.generator.generate(attack_name, inputs)
        
        adv_tensor, true_perturbation = PerturbationOptimizer.optimize(original, raw_perturbation, epsilon)
        
        PerturbationValidator.validate_output(original, adv_tensor, epsilon)
        
        stats = PerturbationAnalyzer.analyze(true_perturbation, epsilon)
        
        res = PerturbationResult(
            adversarial_tensor=adv_tensor,
            perturbation_tensor=true_perturbation,
            verification=stats
        )
        
        if save_research_artifacts:
            heatmap = PerturbationVisualizer.generate_heatmap(true_perturbation, epsilon)
            diff = PerturbationVisualizer.generate_difference(original, adv_tensor)
            overlay = PerturbationVisualizer.generate_overlay(original, heatmap)
            
            metadata = {
                "algorithm": attack_name,
                "engine_version": self.version,
                "epsilon": epsilon,
                "image_size": f"{original.shape[-1]}x{original.shape[-2]}",
                "timestamp": datetime.now(UTC).isoformat(),
                "verification_score": stats.verification_score,
                "coverage": stats.coverage,
                "entropy": stats.entropy
            }
            
            saved = await self.storage.save_artifacts(session_id, true_perturbation, heatmap, diff, overlay, metadata)
            res.heatmap_filename = saved["heatmap"]
            res.difference_filename = saved["difference"]
            res.overlay_filename = saved["overlay"]
            res.perturbation_filename = saved["npy"]
            
        return res
"""
}

for name, content in files.items():
    with open(f"{base_dir}/{name}", "w") as f:
        f.write(content)
        
print("Modules generated successfully.")
