import magic

from app.config.settings import settings
from app.core.exceptions import FileValidationError

ALLOWED_MIME_TYPES = {"image/jpeg", "image/png"}
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png"}

def validate_image_file(filename: str, content: bytes) -> None:
    if not content:
        raise FileValidationError("File is empty (zero-byte).", error_code="FILE_EMPTY")

    if len(content) > settings.max_upload_size_bytes:
        raise FileValidationError(
            f"File size exceeds maximum allowed size of {settings.max_upload_size_bytes / (1024 * 1024)}MB.",
            error_code="FILE_TOO_LARGE"
        )

    # Extension Check
    import os
    ext = os.path.splitext(filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise FileValidationError(
            f"Unsupported file extension. Allowed: {ALLOWED_EXTENSIONS}",
            error_code="UNSUPPORTED_EXTENSION"
        )

    # Magic Bytes MIME Check
    try:
        mime_type = magic.from_buffer(content[:2048], mime=True)
    except Exception as e:
        raise FileValidationError(f"Could not determine MIME type: {e!s}", error_code="MIME_ERROR") from e
        
    if mime_type not in ALLOWED_MIME_TYPES:
        raise FileValidationError(
            f"Unsupported MIME type: {mime_type}. Allowed: {ALLOWED_MIME_TYPES}",
            error_code="UNSUPPORTED_MIME_TYPE"
        )
