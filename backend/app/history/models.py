import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import (
    JSON,
    Boolean,
    CheckConstraint,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.models import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class ProcessingSession(Base):
    __tablename__ = "processing_sessions"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)
    status: Mapped[str] = mapped_column(String, default="created")
    original_image_name: Mapped[str] = mapped_column(String)
    original_image_hash: Mapped[str] = mapped_column(String, index=True)
    image_width: Mapped[int] = mapped_column(Integer)
    image_height: Mapped[int] = mapped_column(Integer)
    image_format: Mapped[str] = mapped_column(String)

    # Relationships
    attacks: Mapped[list["AttackExecution"]] = relationship(
        "AttackExecution", back_populates="session", cascade="all, delete-orphan"
    )
    evaluations: Mapped[list["Evaluation"]] = relationship(
        "Evaluation", back_populates="session", cascade="all, delete-orphan"
    )

    __table_args__ = (
        CheckConstraint(status.in_(["created", "processing", "completed", "failed"]), name="check_valid_status"),
    )


class AttackExecution(Base):
    __tablename__ = "attack_executions"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    session_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("processing_sessions.id", ondelete="CASCADE"), index=True)
    attack_name: Mapped[str] = mapped_column(String)
    attack_version: Mapped[str] = mapped_column(String)
    epsilon: Mapped[float | None] = mapped_column(Float, nullable=True)
    execution_time_ms: Mapped[float | None] = mapped_column(Float, nullable=True)
    device: Mapped[str] = mapped_column(String)
    success: Mapped[bool] = mapped_column(Boolean)
    
    # JSON parameters field for attack-specific configuration
    parameters: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    
    # Advanced verification stats from the Perturbation Analyzer
    verification_data: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)

    # Relationships
    session: Mapped["ProcessingSession"] = relationship("ProcessingSession", back_populates="attacks")


class Evaluation(Base):
    __tablename__ = "evaluations"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    session_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("processing_sessions.id", ondelete="CASCADE"), index=True)
    
    # Image Quality
    psnr: Mapped[float | None] = mapped_column(Float, nullable=True)
    ssim: Mapped[float | None] = mapped_column(Float, nullable=True)
    lpips: Mapped[float | None] = mapped_column(Float, nullable=True)
    
    # Perturbation
    l0: Mapped[float | None] = mapped_column(Float, nullable=True)
    l2: Mapped[float | None] = mapped_column(Float, nullable=True)
    linf: Mapped[float | None] = mapped_column(Float, nullable=True)
    
    # Attack Effectiveness
    confidence_before: Mapped[float | None] = mapped_column(Float, nullable=True)
    confidence_after: Mapped[float | None] = mapped_column(Float, nullable=True)
    confidence_drop: Mapped[float | None] = mapped_column(Float, nullable=True)
    attack_success: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    
    # Performance
    runtime_ms: Mapped[float | None] = mapped_column(Float, nullable=True)
    memory_usage_mb: Mapped[float | None] = mapped_column(Float, nullable=True)
    
    # Extra metrics support
    extra_metrics: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)

    # Relationships
    session: Mapped["ProcessingSession"] = relationship("ProcessingSession", back_populates="evaluations")
    
    __table_args__ = (
        CheckConstraint("psnr >= 0 OR psnr IS NULL", name="check_psnr_positive"),
        CheckConstraint("ssim >= -1 AND ssim <= 1 OR ssim IS NULL", name="check_ssim_range"),
        CheckConstraint("confidence_before >= 0 AND confidence_before <= 1 OR confidence_before IS NULL", name="check_confidence_before_range"),
        CheckConstraint("confidence_after >= 0 AND confidence_after <= 1 OR confidence_after IS NULL", name="check_confidence_after_range"),
    )
