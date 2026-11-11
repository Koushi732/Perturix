import torch
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
