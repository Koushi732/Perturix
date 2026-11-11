import io

from fastapi.testclient import TestClient
from PIL import Image

from app.config.settings import settings


def create_valid_image(format="PNG", size=(100, 100), color="red"):
    img = Image.new("RGB", size, color=color)
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format=format)
    return img_byte_arr.getvalue()

def test_upload_valid_png(client: TestClient):
    content = create_valid_image(format="PNG")
    response = client.post(
        "/api/v1/images/upload",
        files={"image": ("test.png", content, "image/png")}
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["image_format"] == "PNG"
    assert data["status"] == "created"

def test_upload_valid_jpeg(client: TestClient):
    content = create_valid_image(format="JPEG")
    response = client.post(
        "/api/v1/images/upload",
        files={"image": ("test.jpg", content, "image/jpeg")}
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["image_format"] == "JPEG"

def test_upload_oversized_file(client: TestClient):
    # Simulate oversized file by mocking settings or creating a massive array
    original_size = settings.max_upload_size_bytes
    settings.max_upload_size_bytes = 100  # Set limit to 100 bytes temporarily
    try:
        content = create_valid_image(format="PNG")
        response = client.post(
            "/api/v1/images/upload",
            files={"image": ("test.png", content, "image/png")}
        )
        assert response.status_code == 400
        assert "exceeds maximum allowed size" in response.json()["message"]
    finally:
        settings.max_upload_size_bytes = original_size

def test_upload_unsupported_extension(client: TestClient):
    content = create_valid_image(format="PNG")
    response = client.post(
        "/api/v1/images/upload",
        files={"image": ("test.gif", content, "image/gif")} # gif extension
    )
    assert response.status_code == 400
    assert "Unsupported file extension" in response.json()["message"]

def test_upload_corrupted_image(client: TestClient):
    content = b"This is not a real image, but it has enough bytes to pass zero-byte check."
    response = client.post(
        "/api/v1/images/upload",
        files={"image": ("test.png", content, "image/png")}
    )
    assert response.status_code == 400
    # Will fail magic bytes check first
    assert "Unsupported MIME type" in response.json()["message"]

def test_upload_renamed_executable(client: TestClient):
    content = b"MZ\x90\x00\x03\x00\x00\x00" + b"\x00" * 100  # Fake MZ executable header
    response = client.post(
        "/api/v1/images/upload",
        files={"image": ("test.jpg", content, "image/jpeg")}
    )
    assert response.status_code == 400
    assert "Unsupported MIME type" in response.json()["message"]

def test_upload_zero_byte_file(client: TestClient):
    response = client.post(
        "/api/v1/images/upload",
        files={"image": ("test.png", b"", "image/png")}
    )
    assert response.status_code == 400
    assert "File is empty" in response.json()["message"]

def test_upload_path_traversal(client: TestClient):
    content = create_valid_image(format="PNG")
    response = client.post(
        "/api/v1/images/upload",
        files={"image": ("../../../etc/passwd.png", content, "image/png")}
    )
    # Actually, UploadFile.filename strips paths in typical environments, but the UUID generator 
    # completely ignores the original filename except for extension, so path traversal via filename is inherently blocked.
    # We just ensure it uploads safely or strips the bad name.
    assert response.status_code == 200
    # UUID secures the filename, but we just check the original name isn't dangerous
    assert response.json()["data"]["original_image_name"].endswith(".png")
    assert "/" not in response.json()["data"]["original_image_name"]
    assert "\\" not in response.json()["data"]["original_image_name"]
