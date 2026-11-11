import io

from PIL import Image, UnidentifiedImageError

from app.core.exceptions import FileValidationError


def load_and_verify_image(content: bytes) -> dict:
    """
    Safely opens, verifies, and re-opens the image.
    Returns metadata: width, height, format, mode.
    """
    # Protect against decompression bombs
    Image.MAX_IMAGE_PIXELS = 100_000_000  # 100 megapixels max

    try:
        # Step 1: Open
        stream = io.BytesIO(content)
        img = Image.open(stream)
        
        # Step 2: Verify (Catches truncated / corrupted files)
        img.verify()
        
        # Step 3: Re-open for metadata (verify() closes the image)
        stream.seek(0)
        img = Image.open(stream)
        
        width, height = img.size
        
        # Enforce excessive dimensions limit (e.g. max 8192x8192)
        if width > 8192 or height > 8192:
            raise FileValidationError("Image dimensions are too large. Max allowed is 8192x8192.", error_code="DIMENSIONS_TOO_LARGE")

        metadata = {
            "width": width,
            "height": height,
            "format": img.format,
            "mode": img.mode
        }
        return metadata

    except UnidentifiedImageError as e:
        raise FileValidationError("Invalid or corrupted image data.", error_code="CORRUPTED_IMAGE") from e
    except Exception as e:
        if isinstance(e, FileValidationError):
            raise
        raise FileValidationError(f"Error reading image: {e!s}", error_code="IMAGE_READ_ERROR") from e
