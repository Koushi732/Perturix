import logging
import uuid
from typing import Any

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.history.exceptions import HistoryException, SessionNotFoundException
from app.history.repository import (
    AttackRepository,
    EvaluationRepository,
    ProcessingSessionRepository,
)
from app.history.schemas import (
    AttackResponse,
    CreateProcessingSession,
    EvaluationResponse,
    HistoryResponse,
    ProcessingSessionResponse,
    SearchRequest,
)

logger = logging.getLogger(__name__)


class HistoryService:
    def __init__(
        self,
        session_repo: ProcessingSessionRepository,
        attack_repo: AttackRepository,
        eval_repo: EvaluationRepository
    ) -> None:
        self.session_repo = session_repo
        self.attack_repo = attack_repo
        self.eval_repo = eval_repo

    def create_session(self, db: Session, session_data: CreateProcessingSession) -> ProcessingSessionResponse:
        try:
            db_session = self.session_repo.create(db, obj_in=session_data.model_dump())
            logger.info(f"Created ProcessingSession {db_session.id} for image {db_session.original_image_name}")
            return ProcessingSessionResponse.model_validate(db_session)
        except SQLAlchemyError as e:
            logger.error(f"Database error creating session: {e!s}")
            raise HistoryException("Failed to create processing session") from e

    def save_attack(self, db: Session, session_id: uuid.UUID, attack_data: dict[str, Any]) -> AttackResponse:
        try:
            if not self.session_repo.get_by_id(db, session_id):
                raise SessionNotFoundException(f"Session {session_id} not found")
                
            attack_data["session_id"] = session_id
            db_attack = self.attack_repo.create(db, obj_in=attack_data)
            logger.info(f"Saved AttackExecution {db_attack.id} for session {session_id}")
            return AttackResponse.model_validate(db_attack)
        except SQLAlchemyError as e:
            logger.error(f"Database error saving attack: {e!s}")
            raise HistoryException("Failed to save attack execution") from e

    def save_evaluation(self, db: Session, session_id: uuid.UUID, eval_data: dict[str, Any]) -> EvaluationResponse:
        try:
            if not self.session_repo.get_by_id(db, session_id):
                raise SessionNotFoundException(f"Session {session_id} not found")
                
            eval_data["session_id"] = session_id
            db_eval = self.eval_repo.create(db, obj_in=eval_data)
            logger.info(f"Saved Evaluation {db_eval.id} for session {session_id}")
            return EvaluationResponse.model_validate(db_eval)
        except SQLAlchemyError as e:
            logger.error(f"Database error saving evaluation: {e!s}")
            raise HistoryException("Failed to save evaluation") from e

    def get_session(self, db: Session, session_id: uuid.UUID) -> ProcessingSessionResponse:
        try:
            db_session = self.session_repo.get_by_id(db, session_id)
            if not db_session:
                raise SessionNotFoundException(f"Session {session_id} not found")
            return ProcessingSessionResponse.model_validate(db_session)
        except SQLAlchemyError as e:
            raise HistoryException("Database error retrieving session") from e

    def update_session_status(self, db: Session, session_id: uuid.UUID, status: str) -> ProcessingSessionResponse:
        try:
            db_session = self.session_repo.get_by_id(db, session_id)
            if not db_session:
                raise SessionNotFoundException(f"Session {session_id} not found")
            updated = self.session_repo.update(db, db_obj=db_session, obj_in={"status": status})
            return ProcessingSessionResponse.model_validate(updated)
        except SQLAlchemyError as e:
            raise HistoryException("Database error updating session status") from e

    def search_history(self, db: Session, request: SearchRequest) -> HistoryResponse:
        try:
            sessions = self.session_repo.filter(
                db,
                status=request.status,
                image_hash=request.image_hash,
                skip=request.skip,
                limit=request.limit
            )
            total = self.session_repo.count(
                db,
                status=request.status,
                image_hash=request.image_hash
            )
            items = [ProcessingSessionResponse.model_validate(s) for s in sessions]
            return HistoryResponse(
                items=items,
                total=total,
                skip=request.skip,
                limit=request.limit
            )
        except SQLAlchemyError as e:
            logger.error(f"Database error searching history: {e!s}")
            raise HistoryException("Failed to retrieve processing history") from e
