import pytest
from fastapi.testclient import TestClient

from app.database.models import Base
from app.database.session import engine
from app.main import app


@pytest.fixture
def client():
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c
