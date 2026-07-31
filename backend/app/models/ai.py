from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.mixins import UUIDPrimaryKeyMixin

# job/prediction status values used across this module
JOB_STATUS_QUEUED = "QUEUED"
JOB_STATUS_RUNNING = "RUNNING"
JOB_STATUS_COMPLETED = "COMPLETED"
JOB_STATUS_FAILED = "FAILED"


class AIJob(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "ai_jobs"

    document_version_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("document_versions.id", ondelete="CASCADE"), nullable=False
    )
    job_type: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False, default=JOB_STATUS_QUEUED)
    priority: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    model_identifier: Mapped[str | None] = mapped_column(String(128), nullable=True)
    prompt_version: Mapped[str | None] = mapped_column(String(32), nullable=True)

    queued_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)

    raw_response: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    validated_response: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    error_code: Mapped[str | None] = mapped_column(String(64), nullable=True)
    error_message: Mapped[str | None] = mapped_column(String(1024), nullable=True)

    predictions: Mapped[list["AIFieldPrediction"]] = relationship(
        back_populates="ai_job", cascade="all, delete-orphan"
    )


class AIFieldPrediction(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "ai_field_predictions"

    ai_job_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ai_jobs.id", ondelete="CASCADE"), nullable=False
    )
    field_code: Mapped[str] = mapped_column(String(64), nullable=False)
    proposed_value: Mapped[dict] = mapped_column(JSONB, nullable=False)
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    source_snippet: Mapped[str | None] = mapped_column(String(512), nullable=True)
    is_reviewed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    ai_job: Mapped["AIJob"] = relationship(back_populates="predictions")
    feedback: Mapped[list["AIFeedback"]] = relationship(back_populates="prediction", cascade="all, delete-orphan")


class AIFeedback(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "ai_feedback"

    ai_field_prediction_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ai_field_predictions.id", ondelete="CASCADE"), nullable=False
    )
    proposed_value: Mapped[dict] = mapped_column(JSONB, nullable=False)
    confirmed_value: Mapped[dict] = mapped_column(JSONB, nullable=False)
    was_correct: Mapped[bool] = mapped_column(Boolean, nullable=False)
    correction_reason: Mapped[str | None] = mapped_column(String(512), nullable=True)
    corrected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    corrected_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)

    prediction: Mapped["AIFieldPrediction"] = relationship(back_populates="feedback")
