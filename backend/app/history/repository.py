import uuid
from typing import Any, Generic, TypeVar

from sqlalchemy import asc, desc, select
from sqlalchemy.orm import Session

from app.database.models import Base
from app.history.models import AttackExecution, Evaluation, ProcessingSession

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    def __init__(self, model: type[ModelType]) -> None:
        self.model = model

    def get_by_id(self, db: Session, id: uuid.UUID) -> ModelType | None:
        return db.get(self.model, id)

    def create(self, db: Session, *, obj_in: dict[str, Any]) -> ModelType:
        db_obj = self.model(**obj_in)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, *, db_obj: ModelType, obj_in: dict[str, Any]) -> ModelType:
        for field, value in obj_in.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, *, id: uuid.UUID) -> ModelType | None:
        db_obj = db.get(self.model, id)
        if db_obj:
            db.delete(db_obj)
            db.commit()
        return db_obj

    def list(
        self, db: Session, *, skip: int = 0, limit: int = 100, order_by: str = "id", descending: bool = True
    ) -> list[ModelType]:
        order_col = getattr(self.model, order_by, None)
        if order_col is None:
            order_col = getattr(self.model, "id")  # noqa: B009
            
        stmt = select(self.model)
        if descending:
            stmt = stmt.order_by(desc(order_col))
        else:
            stmt = stmt.order_by(asc(order_col))
            
        stmt = stmt.offset(skip).limit(limit)
        return list(db.scalars(stmt).all())


class ProcessingSessionRepository(BaseRepository[ProcessingSession]):
    def __init__(self) -> None:
        super().__init__(ProcessingSession)
        
    def filter(
        self,
        db: Session,
        *,
        status: str | None = None,
        image_hash: str | None = None,
        skip: int = 0,
        limit: int = 100
    ) -> list[ProcessingSession]:
        stmt = select(ProcessingSession)
        if status:
            stmt = stmt.where(ProcessingSession.status == status)
        if image_hash:
            stmt = stmt.where(ProcessingSession.original_image_hash == image_hash)
            
        stmt = stmt.order_by(desc(ProcessingSession.created_at)).offset(skip).limit(limit)
        return list(db.scalars(stmt).all())
        
    def count(self, db: Session, *, status: str | None = None, image_hash: str | None = None) -> int:
        from sqlalchemy import func
        stmt = select(func.count()).select_from(ProcessingSession)
        if status:
            stmt = stmt.where(ProcessingSession.status == status)
        if image_hash:
            stmt = stmt.where(ProcessingSession.original_image_hash == image_hash)
        return db.scalar(stmt) or 0


class AttackRepository(BaseRepository[AttackExecution]):
    def __init__(self) -> None:
        super().__init__(AttackExecution)


class EvaluationRepository(BaseRepository[Evaluation]):
    def __init__(self) -> None:
        super().__init__(Evaluation)
