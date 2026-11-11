from collections.abc import Generator

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.database.models import Base
from app.history.repository import (
    AttackRepository,
    EvaluationRepository,
    ProcessingSessionRepository,
)


@pytest.fixture
def db_session() -> Generator[Session, None, None]:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)


def test_processing_session_crud(db_session: Session) -> None:
    repo = ProcessingSessionRepository()
    
    # Create
    session_in = {
        "original_image_name": "test.png",
        "original_image_hash": "abc123hash",
        "image_width": 224,
        "image_height": 224,
        "image_format": "png"
    }
    db_obj = repo.create(db_session, obj_in=session_in)
    assert db_obj.id is not None
    assert db_obj.status == "created"
    
    # Read
    db_obj2 = repo.get_by_id(db_session, db_obj.id)
    assert db_obj2 is not None
    assert db_obj2.original_image_hash == "abc123hash"
    
    # Update
    db_obj3 = repo.update(db_session, db_obj=db_obj2, obj_in={"status": "completed"})
    assert db_obj3.status == "completed"
    
    # List / filter
    lst = repo.filter(db_session, status="completed")
    assert len(lst) == 1
    
    count = repo.count(db_session, status="completed")
    assert count == 1
    
    # Delete
    repo.delete(db_session, id=db_obj.id)
    assert repo.get_by_id(db_session, db_obj.id) is None


def test_attack_and_eval_crud(db_session: Session) -> None:
    repo = ProcessingSessionRepository()
    attack_repo = AttackRepository()
    eval_repo = EvaluationRepository()
    
    db_sess = repo.create(db_session, obj_in={
        "original_image_name": "test.png",
        "original_image_hash": "hash",
        "image_width": 100,
        "image_height": 100,
        "image_format": "png"
    })
    
    db_atk = attack_repo.create(db_session, obj_in={
        "session_id": db_sess.id,
        "attack_name": "FGSM",
        "attack_version": "1.0",
        "device": "cpu",
        "success": True,
        "parameters": {"epsilon": 0.05}
    })
    
    db_eval = eval_repo.create(db_session, obj_in={
        "session_id": db_sess.id,
        "psnr": 30.5
    })
    
    assert db_atk.id is not None
    assert db_eval.id is not None
    
    # Test relationship mapping
    db_sess_ref = repo.get_by_id(db_session, db_sess.id)
    assert db_sess_ref is not None
    assert len(db_sess_ref.attacks) == 1
    assert len(db_sess_ref.evaluations) == 1
    assert db_sess_ref.attacks[0].parameters == {"epsilon": 0.05}
