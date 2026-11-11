from functools import lru_cache

from app.config.settings import Settings
from app.config.settings import settings as global_settings


@lru_cache
def get_settings() -> Settings:
    return global_settings
