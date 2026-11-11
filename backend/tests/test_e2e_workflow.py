import os
from collections.abc import Generator

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.database.models import Base
from app.database.session import get_db
from app.main import app

engine = create_engine(
    "sqlite:///:memory:", 
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db() -> Generator[Session, None, None]:
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

def test_full_workflow() -> None:
    # 1. Upload
    os.makedirs("tests/assets", exist_ok=True)
    test_img_path = "tests/assets/temp_test.jpg"
    
    from PIL import Image
    Image.new('RGB', (100, 100), color = 'red').save(test_img_path)
    
    with open(test_img_path, "rb") as f:
        res = client.post("/api/v1/images/upload", files={"image": ("test.jpg", f, "image/jpeg")})
    assert res.status_code == 200, res.text
    data = res.json()["data"]
    session_id = data["id"]
    assert session_id is not None
    
    # 2. Execute Attack
    attack_payload = {
        "session_id": session_id,
        "attack_name": "FGSM",
        "parameters": {"epsilon": 0.05}
    }
    res = client.post("/api/v1/attacks/execute", json=attack_payload)
    assert res.status_code == 200, res.text
    
    # 3. Evaluation
    eval_payload = {
        "session_id": session_id
    }
    res = client.post("/api/v1/evaluation/execute", json=eval_payload)
    assert res.status_code == 200, res.text
    
    # 4. History
    res = client.get("/api/v1/history/")
    assert res.status_code == 200, res.text
    assert len(res.json()["data"]["items"]) == 1
    
    # 5. Get Session
    res = client.get(f"/api/v1/history/{session_id}")
    assert res.status_code == 200, res.text
    
    if os.path.exists(test_img_path):
        os.remove(test_img_path)
