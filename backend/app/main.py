import sys
from contextlib import asynccontextmanager
from datetime import UTC

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.attacks import endpoints as attacks_endpoints
from app.api.v1.evaluation import endpoints as evaluation_endpoints
from app.api.v1.history import endpoints as history_endpoints
from app.api.v1.images import endpoints as images_endpoints
from app.api.v1.system import endpoints as system_endpoints
from app.config.settings import settings
from app.core.exceptions import ConfigurationError, PerturixException
from app.dependencies.logger import get_logger
from app.middleware.request_middleware import RequestMiddleware
from app.schemas.common.error import ErrorResponse
from app.schemas.common.metadata import ResponseMetadata

logger = get_logger()

def validate_configuration():
    """Validates required configurations and directories before startup."""
    logger.info("Validating system configuration...")
    
    dirs_to_check = [settings.upload_dir, settings.output_dir, settings.log_dir]
    for d in dirs_to_check:
        try:
            d.mkdir(parents=True, exist_ok=True)
            # Check write permission by touching a temporary file
            test_file = d / ".write_test"
            test_file.touch()
            test_file.unlink()
        except OSError as e:
            logger.error(f"Configuration Validation Failed: Cannot write to {d}. Error: {e!s}")
            raise ConfigurationError(f"Directory validation failed for {d}")
            
    logger.info("System configuration validated successfully.")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    try:
        validate_configuration()
    except ConfigurationError as ce:
        logger.critical(f"Startup aborted due to configuration error: {ce.detail}")
        sys.exit(1)
        
    logger.info(f"Starting {settings.app_name} v{settings.version}")
    yield
    # Shutdown
    logger.info(f"Shutting down {settings.app_name}")

def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        description="Backend for the Perturix Adaptive Image Immunization Framework",
        version=settings.version,
        lifespan=lifespan
    )
    
    # Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Request-ID", "X-Process-Time"]
    )
    
    app.add_middleware(RequestMiddleware)
    
    # Exception Handlers
    @app.exception_handler(PerturixException)
    async def perturix_exception_handler(request, exc: PerturixException):
        from datetime import datetime

        from fastapi.responses import JSONResponse
        
        request_id = request.headers.get("X-Request-ID", "UNKNOWN")
        error_response = ErrorResponse(
            success=False,
            message=exc.detail,
            data=None,
            metadata=ResponseMetadata(request_id=request_id, error_code=exc.error_code),
            timestamp=datetime.now(UTC).isoformat()
        )
        return JSONResponse(
            status_code=exc.status_code,
            content=error_response.model_dump()
        )
    
    # OpenAPI Customization (Global default responses)
    app.router.responses = {
        400: {"model": ErrorResponse, "description": "Bad Request"},
        404: {"model": ErrorResponse, "description": "Not Found"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    }
    
    # Routers
    app.include_router(system_endpoints.router, prefix=settings.api_v1_prefix)
    app.include_router(images_endpoints.router, prefix=settings.api_v1_prefix)
    app.include_router(attacks_endpoints.router, prefix=settings.api_v1_prefix)
    app.include_router(evaluation_endpoints.router, prefix=settings.api_v1_prefix)
    app.include_router(history_endpoints.router, prefix=settings.api_v1_prefix)
    
    return app

app = create_app()
