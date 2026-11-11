import os

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "Perturix API"
    API_V1_STR: str = "/api/v1"
    
    # Upload Configuration
    UPLOAD_DIR: str = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads")
    TEMP_DIR: str = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "temp")
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10 MB
    ALLOWED_EXTENSIONS: set = {".png", ".jpg", ".jpeg"}
    ALLOWED_CONTENT_TYPES: set = {"image/png", "image/jpeg"}

    class Config:
        env_file = ".env"

settings = Settings()

# Ensure directories exist
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.TEMP_DIR, exist_ok=True)
