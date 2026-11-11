from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Perturix Backend"
    version: str = "1.0.0"
    
    # Directories
    base_dir: Path = Path(__file__).resolve().parent.parent.parent
    upload_dir: Path = base_dir / "uploads"
    output_dir: Path = base_dir / "outputs"
    log_dir: Path = base_dir / "logs"
    
    # Security / API
    secret_key: str  # Required
    environment: str = "development"
    api_v1_prefix: str = "/api/v1"
    cors_origins: list[str] = ["http://localhost", "http://localhost:5173", "http://localhost:3000"]
    max_upload_size_bytes: int = 10 * 1024 * 1024 # 10MB
    
    model_config = SettingsConfigDict(env_file=".env", env_ignore_empty=True, extra="ignore")

settings = Settings()  # type: ignore[call-arg]
