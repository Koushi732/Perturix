import torch
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
