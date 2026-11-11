import logging
import uuid
from typing import Any

from app.evaluation.context import EvaluationContext
from app.evaluation.registry import MetricRegistry
from app.evaluation.result import EvaluationResult

logger = logging.getLogger(__name__)


class EvaluationEngine:
    def __init__(self, registry: MetricRegistry, version: str = "1.0.0") -> None:
        self.registry = registry
        self.version = version

    def evaluate(
        self,
        context: EvaluationContext,
        attack_name: str,
        attack_version: str,
        image_name: str,
    ) -> EvaluationResult:
        """
        Orchestrates metric execution securely.
        Aggregates results into a single EvaluationResult.
        """
        eval_id = uuid.uuid4()
        
        result_dict: dict[str, Any] = {
            "evaluation_id": eval_id,
            "attack_name": attack_name,
            "attack_version": attack_version,
            "image_name": image_name,
            "evaluator_version": self.version,
            "warnings": [],
            "notes": [],
            "metric_versions": {}
        }
        
        # Inject raw performance numbers (metrics parse these if needed)
        if context.attack_execution_time_ms is not None:
             result_dict["execution_time_ms"] = context.attack_execution_time_ms
        if context.attack_memory_usage_mb is not None:
             result_dict["memory_usage_mb"] = context.attack_memory_usage_mb

        metrics = self.registry.get_all()
        for metric in metrics:
            result_dict["metric_versions"][metric.name] = metric.version
            
            try:
                # Execution lifecycle
                metric.initialize()
                metric.validate(context)
                
                # Computation
                val = metric.compute(context)
                
                if isinstance(val, dict):
                    result_dict.update(val)
                elif val is not None:
                    field_name = metric.name.lower()
                    if field_name in EvaluationResult.model_fields:
                        result_dict[field_name] = val
                    else:
                        result_dict["notes"].append(f"{metric.name}: {val}")
                        
                logger.info(f"Evaluation metric '{metric.name}' v{metric.version} completed successfully.")
                
            except Exception as e:  # noqa: BLE001
                err_msg = f"Metric {metric.name} failed: {e!s}"
                logger.error(f"Evaluation ID {eval_id} | Attack {attack_name} | {err_msg}")
                result_dict["warnings"].append(err_msg)
            finally:
                metric.cleanup()
                
        return EvaluationResult(**result_dict)
