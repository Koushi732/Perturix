import io
import uuid
from typing import Any

from fastapi import UploadFile
from PIL import Image
from sqlalchemy.orm import Session

from app.ai_engine.pipeline import PipelineExecutor
from app.ai_engine.registry import AttackRegistry
from app.core.exceptions import PerturixException
from app.dependencies.logger import get_logger
from app.dependencies.storage import get_storage_provider
from app.evaluation.context import EvaluationContext
from app.evaluation.engine import EvaluationEngine
from app.history.exceptions import SessionNotFoundException
from app.history.schemas import (
    AttackResponse,
    CreateProcessingSession,
    EvaluationResponse,
    ProcessingSessionResponse,
)
from app.history.service import HistoryService
from app.services.ai.model import ResNet50VictimModel
from app.services.image.tensor import pil_to_tensor, tensor_to_pil
from app.services.upload.service import process_upload

logger = get_logger()


class AttackWorkflowService:
    def __init__(
        self,
        history_service: HistoryService,
        pipeline: PipelineExecutor,
        attack_registry: AttackRegistry,
        evaluation_engine: EvaluationEngine,
    ) -> None:
        self.history_service = history_service
        self.pipeline = pipeline
        self.attack_registry = attack_registry
        self.evaluation_engine = evaluation_engine
        self.storage = get_storage_provider()

    async def handle_upload(self, db: Session, file: UploadFile) -> ProcessingSessionResponse:
        session_id = uuid.uuid4()
        upload_data = await process_upload(file, file_uuid=session_id)
        
        import os
        safe_filename = os.path.basename(file.filename or "unknown")
        safe_filename = safe_filename.split("/")[-1].split("\\")[-1]
        
        create_data = CreateProcessingSession(
            id=session_id,
            original_image_name=safe_filename,
            original_image_hash=upload_data.sha256,
            image_width=upload_data.width,
            image_height=upload_data.height,
            image_format=upload_data.format,
            status="created"
        )
        
        return self.history_service.create_session(db, create_data)

    async def execute_attack(self, db: Session, session_id: uuid.UUID, attack_name: str, parameters: dict[str, Any]) -> AttackResponse:
        session = self.history_service.get_session(db, session_id)
        if not session:
            raise SessionNotFoundException("Session not found")
            
        self.history_service.update_session_status(db, session_id, "processing")
        
        # Determine image file extension from format
        ext = ".jpg" if session.image_format.lower() in ("jpg", "jpeg") else ".png"
        filename = f"{session_id}{ext}"
        
        # Load image via storage provider
        try:
            image_data = await self.storage.get_file(filename)
            if isinstance(image_data, bytes):
                img = Image.open(io.BytesIO(image_data))
            else:
                img = Image.open(image_data)
            
            input_tensor = pil_to_tensor(img).unsqueeze(0).clone().detach().requires_grad_(True)
        except Exception as e:
            self.history_service.update_session_status(db, session_id, "failed")
            raise PerturixException(status_code=500, detail=f"Failed to load image: {e!s}", error_code="IMAGE_LOAD_ERROR") from e
            
        # Execute Attack
        try:
            from app.protection.engine import ProtectionEngine
            
            model = ResNet50VictimModel()
            engine = ProtectionEngine(self.pipeline)
            
            epsilon = parameters.get("epsilon", 0.03)
            save_artifacts = parameters.get("save_research_artifacts", False)
            
            res = await engine.process(
                attack_name, 
                {"tensor": input_tensor, "model": model, **parameters},
                epsilon, 
                save_artifacts, 
                str(session_id)
            )
            
            # Save adversarial image
            adv_ext = ".png" # always save adversarial as png for lossless
            adv_filename = f"{session_id}_adv{adv_ext}"
            adv_tensor = res.adversarial_tensor
            if adv_tensor.ndim == 4:
                adv_tensor = adv_tensor.squeeze(0)
            adv_img = tensor_to_pil(adv_tensor)
            
            buf = io.BytesIO()
            adv_img.save(buf, format="PNG")
            buf.seek(0)
            await self.storage.save_file(adv_filename, buf)
            
            # Save history
            attack_data = {
                "attack_name": attack_name,
                "attack_version": self.attack_registry.lookup(attack_name).version,
                "epsilon": parameters.get("epsilon"),
                "execution_time_ms": 0.0,
                "device": str(adv_tensor.device),
                "success": res.verification.status != "WEAK",
                "parameters": parameters,
                "verification_data": res.verification.model_dump()
            }
            
            atk_res = self.history_service.save_attack(db, session_id, attack_data)
            self.history_service.update_session_status(db, session_id, "completed")
            return atk_res
            
        except Exception as e:
            self.history_service.update_session_status(db, session_id, "failed")
            logger.error(f"Attack failed: {e!s}")
            raise PerturixException(status_code=500, detail=f"Attack execution failed: {e!s}", error_code="ATTACK_ERROR") from e

    async def evaluate_session(self, db: Session, session_id: uuid.UUID) -> EvaluationResponse:
        session = self.history_service.get_session(db, session_id)
        if not session:
            raise SessionNotFoundException("Session not found")
            
        if not session.attacks:
            raise PerturixException(status_code=400, detail="No attacks found for this session to evaluate.", error_code="NO_ATTACK")
            
        ext = ".jpg" if session.image_format.lower() in ("jpg", "jpeg") else ".png"
        orig_filename = f"{session_id}{ext}"
        adv_filename = f"{session_id}_adv.png"
        
        try:
            orig_data = await self.storage.get_file(orig_filename)
            adv_data = await self.storage.get_file(adv_filename)
            
            orig_tensor = pil_to_tensor(Image.open(orig_data)).unsqueeze(0)
            adv_tensor = pil_to_tensor(Image.open(adv_data)).unsqueeze(0)
        except Exception as e:
            raise PerturixException(status_code=500, detail=f"Failed to load images for evaluation: {e!s}", error_code="IMAGE_LOAD_ERROR") from e
            
        atk = session.attacks[-1]
        
        # Calculate probabilities for Confidence Metric
        model = ResNet50VictimModel()
        orig_probs = model.predict(orig_tensor)
        adv_probs = model.predict(adv_tensor)
            
        ctx = EvaluationContext(
            original_tensor=orig_tensor,
            adversarial_tensor=adv_tensor,
            model=model,
            original_probabilities=orig_probs,
            adversarial_probabilities=adv_probs,
            attack_execution_time_ms=atk.execution_time_ms
        )
        
        try:
            eval_result = self.evaluation_engine.evaluate(
                context=ctx,
                attack_name=atk.attack_name,
                attack_version=atk.attack_version,
                image_name=session.original_image_name
            )
            
            eval_data: dict[str, Any] = {
                "psnr": eval_result.psnr,
                "ssim": eval_result.ssim,
                "lpips": eval_result.lpips,
                "l0": eval_result.l0,
                "l2": eval_result.l2,
                "linf": eval_result.linf,
                "confidence_before": eval_result.confidence_before,
                "confidence_after": eval_result.confidence_after,
                "confidence_drop": eval_result.confidence_drop,
                "attack_success": eval_result.attack_success,
                "runtime_ms": eval_result.execution_time_ms,
                "memory_usage_mb": eval_result.memory_usage_mb,
                "extra_metrics": {}
            }
            
            return self.history_service.save_evaluation(db, session_id, eval_data)
        except Exception as e:
            logger.error(f"Evaluation failed: {e!s}")
            raise PerturixException(status_code=500, detail=f"Evaluation failed: {e!s}", error_code="EVAL_ERROR") from e
