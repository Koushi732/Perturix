import torch
import numpy as np
import cv2
from PIL import Image

class PerturbationVisualizer:
    @staticmethod
    def tensor_to_cv2(t: torch.Tensor) -> np.ndarray:
        arr = t.squeeze(0).permute(1, 2, 0).detach().cpu().numpy() if t.ndim == 4 else t.permute(1, 2, 0).detach().cpu().numpy()
        arr = np.clip(arr * 255, 0, 255).astype(np.uint8)
        return cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)
        
    @staticmethod
    def generate_heatmap(perturbation: torch.Tensor, epsilon: float) -> Image.Image:
        p = perturbation.squeeze(0).permute(1, 2, 0).detach().cpu().numpy() if perturbation.ndim == 4 else perturbation.permute(1, 2, 0).detach().cpu().numpy()
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
