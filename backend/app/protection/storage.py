import os
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
        np.save(os.path.join(self.base_dir, npy_name), perturbation.detach().cpu().numpy())
        
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
