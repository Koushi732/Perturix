import uuid
from collections.abc import Generator

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.database.models import Base
from app.history.exceptions import SessionNotFoundException
from app.history.repository import (
    AttackRepository,
    EvaluationRepository,
    ProcessingSessionRepository,
)
from app.history.schemas import CreateProcessingSession, SearchRequest
from app.history.service import HistoryService


@pytest.fixture
def db_session() -> Generator[Session, None, None]:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def history_service() -> HistoryService:
    return HistoryService(
        ProcessingSessionRepository(),
        AttackRepository(),
        EvaluationRepository()
    )


def test_service_create_and_retrieve_session(db_session: Session, history_service: HistoryService) -> None:
    data = CreateProcessingSession(
        original_image_name="test.png",
        original_image_hash="abc",
        image_width=100,
        image_height=100,
        image_format="png"
    )
    res = history_service.create_session(db_session, data)
    
    res2 = history_service.get_session(db_session, res.id)
    assert res2.original_image_hash == "abc"


def test_service_save_attack(db_session: Session, history_service: HistoryService) -> None:
    data = CreateProcessingSession(
        original_image_name="test.png",
        original_image_hash="abc",
        image_width=100,
        image_height=100,
        image_format="png"
    )
    sess = history_service.create_session(db_session, data)
    
    attack_data = {
        "attack_name": "FGSM",
        "attack_version": "1.0",
        "device": "cpu",
        "success": True
    }
    atk = history_service.save_attack(db_session, sess.id, attack_data)
    assert atk.attack_name == "FGSM"


def test_service_missing_session(db_session: Session, history_service: HistoryService) -> None:
    with pytest.raises(SessionNotFoundException):
        history_service.save_attack(
            db_session, uuid.uuid4(),
            {"attack_name": "FGSM", "attack_version": "1.0", "device": "cpu", "success": True}
        )


def test_service_save_evaluation(db_session: Session, history_service: HistoryService) -> None:
    data = CreateProcessingSession(
        original_image_name="test.png",
        original_image_hash="abc",
        image_width=100,
        image_height=100,
        image_format="png"
    )
    sess = history_service.create_session(db_session, data)
    
    eval_data = {
        "psnr": 30.0,
        "attack_success": True
    }
    ev = history_service.save_evaluation(db_session, sess.id, eval_data)
    assert ev.psnr == 30.0


def test_service_search(db_session: Session, history_service: HistoryService) -> None:
    data = CreateProcessingSession(
        original_image_name="test.png",
        original_image_hash="hash1",
        image_width=100,
        image_height=100,
        image_format="png"
    )
    history_service.create_session(db_session, data)
    
    req = SearchRequest(image_hash="hash1")
    res = history_service.search_history(db_session, req)
    assert res.total == 1
    
def test_update_status(db_session: Session, history_service: HistoryService) -> None:
    data = CreateProcessingSession(
        original_image_name="test.png",
        original_image_hash="hash1",
        image_width=100,
        image_height=100,
        image_format="png"
    )
    sess = history_service.create_session(db_session, data)
    history_service.update_session_status(db_session, sess.id, "processing")
    
    updated = history_service.get_session(db_session, sess.id)
    assert updated.status == "processing"
