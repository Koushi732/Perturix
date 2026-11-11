import os
import time
import uuid
from datetime import UTC, datetime

import magic
from fastapi import UploadFile

from app.dependencies.logger import get_logger
from app.dependencies.storage import get_storage_provider
from app.schemas.responses.upload import UploadResponseData
from app.services.image.loader import load_and_verify_image
from app.services.image.validator import validate_image_file
from app.utils.hash import calculate_sha256

logger = get_logger()

async def process_upload(file: UploadFile, file_uuid: uuid.UUID | None = None) -> UploadResponseData:
    start_time = time.time()
    
    # 1. Read Bytes
    content = await file.read()
    
    # 2. Validate Image Safety & Limits
    filename = os.path.basename(file.filename or "unknown")
    validate_image_file(filename, content)
    logger.info("Validation successful.")
    
    # 3. Image Verification & Metadata Extraction (open -> verify -> reopen)
    metadata = load_and_verify_image(content)
    
    # 4. SHA-256
    sha256_hash = calculate_sha256(content)
    
    # 5. Storage
    if file_uuid is None:
        file_uuid = uuid.uuid4()
    file_uuid_str = str(file_uuid)
    ext = os.path.splitext(filename)[1].lower()
    secure_filename = f"{file_uuid_str}{ext}"
    
    storage_provider = get_storage_provider()
    
    storage_start = time.time()
    storage_path = await storage_provider.save_file(secure_filename, content)  # type: ignore[arg-type]
    storage_duration = (time.time() - storage_start) * 1000
    logger.debug(f"File stored at {storage_path} in {storage_duration:.2f}ms")
    
    mime_type = magic.from_buffer(content[:2048], mime=True)
    
    response_data = UploadResponseData(
        uuid=file_uuid_str,
        sha256=sha256_hash,
        filename=secure_filename,
        width=metadata["width"],
        height=metadata["height"],
        size=len(content),
        mime=mime_type,
        format=metadata["format"],
        uploaded_at=datetime.now(UTC).isoformat(),
        processing_state="uploaded"
    )
    
    total_duration = (time.time() - start_time) * 1000
    logger.info(f"Upload completed: {secure_filename} | UUID: {file_uuid_str} | SHA256: {sha256_hash} | Size: {len(content)} bytes | Total Duration: {total_duration:.2f}ms")
    
    return response_data
