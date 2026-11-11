import logging
import time
import uuid
from typing import Any

from app.ai_engine.models import AttackResult
from app.ai_engine.registry import IAttackRegistry
from app.config.ai import ai_settings
from app.core.exceptions import AttackExecutionException, AttackValidationException

logger = logging.getLogger(__name__)

class PipelineExecutor:
    def __init__(self, registry: IAttackRegistry):
        self.registry = registry

    def execute_pipeline(self, attack_name: str, inputs: dict[str, Any]) -> AttackResult:
        """
        Orchestrates the rigid execution flow of an attack.
        Flow: Resolve -> Validate -> Initialize -> Execute -> Cleanup (finally) -> Return
        """
        attack_uuid = str(uuid.uuid4())
        
        lookup_start = time.time()
        attack = self.registry.lookup(attack_name)
        lookup_time = (time.time() - lookup_start) * 1000
        
        device = ai_settings.device
        attack_version = attack.version
        
        logger.info(
            f"Resolved attack '{attack_name}' v{attack_version} (UUID: {attack_uuid}) "
            f"on device '{device}' in {lookup_time:.2f}ms"
        )

        exec_start = time.time()
        success = False
        warnings = []
        errors = []
        result = None
        initialized = False

        try:
            # 1. Validate
            try:
                attack.validate(inputs)
            except Exception as e:
                logger.error(f"[Stage: Validate] Failed for {attack_name} v{attack_version}. Reason: {e!s}")
                raise AttackValidationException(str(e)) from e
                
            # 2. Initialize
            try:
                attack.initialize()
                initialized = True
            except Exception as e:
                logger.error(f"[Stage: Initialize] Failed for {attack_name} v{attack_version}. Reason: {e!s}")
                raise AttackExecutionException(f"Initialization failed: {e!s}") from e

            # 3. Execute
            try:
                result = attack.execute(inputs)
                success = result.success
                if result.warnings:
                    warnings.extend(result.warnings)
                if result.errors:
                    errors.extend(result.errors)
            except Exception as e:
                logger.error(f"[Stage: Execute] Failed for {attack_name} v{attack_version}. Reason: {e!s}")
                raise AttackExecutionException(f"Execution failed: {e!s}") from e
                
        finally:
            # 4. Cleanup
            if initialized:
                cleanup_start = time.time()
                try:
                    attack.cleanup()
                except Exception as e:  # noqa: BLE001
                    logger.error(f"[Stage: Cleanup] Failed for {attack_name} v{attack_version}. Reason: {e!s}")
                cleanup_time = (time.time() - cleanup_start) * 1000
                logger.info(f"Cleanup for '{attack_name}' took {cleanup_time:.2f}ms")

            total_exec_time = (time.time() - exec_start) * 1000
            
            if result:
                result.execution_time_ms = total_exec_time
            
            logger.info(
                f"Pipeline finished for '{attack_name}' v{attack_version}. "
                f"Success: {success}. Execution Time: {total_exec_time:.2f}ms"
            )

        return result
