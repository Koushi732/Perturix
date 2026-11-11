from pydantic_settings import BaseSettings, SettingsConfigDict


class AISettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_ignore_empty=False, 
        extra="ignore",
        env_prefix="AI_"
    )
    
    device: str = "cpu"
    precision: str = "float32"
    seed: int = 42
    deterministic_mode: bool = True
    tensor_memory_limits: int = 1024 * 1024 * 1024  # 1 GB
    
    enable_cuda: bool = False
    fallback_to_cpu: bool = True
    allow_mixed_precision: bool = False

ai_settings = AISettings()
