from pydantic import BaseModel, Field


class UploadResponseData(BaseModel):
    uuid: str = Field(..., description="The generated UUID for the uploaded file.")
    sha256: str = Field(..., description="SHA-256 hash of the original file.")
    filename: str = Field(..., description="The secure storage filename.")
    width: int = Field(..., description="Image width in pixels.")
    height: int = Field(..., description="Image height in pixels.")
    size: int = Field(..., description="File size in bytes.")
    mime: str = Field(..., description="Detected MIME type (via magic bytes).")
    format: str = Field(..., description="Detected image format (e.g., JPEG, PNG).")
    uploaded_at: str = Field(..., description="ISO-8601 timestamp of the upload.")
    processing_state: str = Field(default="uploaded", description="Current state in the pipeline.")
