import logging
import sys

from app.config.settings import settings


def setup_logger():
    # Ensure log directory exists
    settings.log_dir.mkdir(parents=True, exist_ok=True)
    
    logger = logging.getLogger("perturix")
    logger.setLevel(logging.INFO)
    
    # Avoid duplicate handlers
    if not logger.handlers:
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - [%(correlation_id)s] - %(message)s"
        )
        
        # Console handler
        ch = logging.StreamHandler(sys.stdout)
        ch.setFormatter(formatter)
        logger.addHandler(ch)
        
        # File handler
        fh = logging.FileHandler(settings.log_dir / "app.log")
        fh.setFormatter(formatter)
        logger.addHandler(fh)
        
    return logger

class ContextFilter(logging.Filter):
    """
    This is a filter which injects the request ID into the log.
    For simplicity in this milestone without contextvars, we might just default it.
    We will use ContextVars for request_id in middleware.
    """
    def filter(self, record):
        from app.middleware.request_context import request_id_var
        record.correlation_id = request_id_var.get("SYSTEM")
        return True

logger = setup_logger()
logger.addFilter(ContextFilter())

def get_logger() -> logging.Logger:
    return logger
