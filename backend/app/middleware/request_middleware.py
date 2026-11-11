import time
import uuid

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from app.dependencies.logger import get_logger
from app.middleware.request_context import request_id_var

logger = get_logger()

class RequestMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request_id_var.set(request_id)
        
        start_time = time.time()
        
        logger.info(f"Incoming request: {request.method} {request.url.path}")
        
        try:
            response = await call_next(request)
            process_time = (time.time() - start_time) * 1000
            response.headers["X-Process-Time"] = str(process_time)
            response.headers["X-Request-ID"] = request_id
            
            # Security Headers
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["X-Frame-Options"] = "DENY"
            response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
            response.headers["Content-Security-Policy"] = "default-src 'self'"
            response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
            
            logger.info(f"Completed request: {request.method} {request.url.path} - Status: {response.status_code} - {process_time:.2f}ms")
            return response
        except Exception as e:
            process_time = (time.time() - start_time) * 1000
            logger.error(f"Failed request: {request.method} {request.url.path} - {process_time:.2f}ms - Error: {e!s}")
            raise
