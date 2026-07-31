from __future__ import annotations

import uuid
from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.mixins import UUIDPrimaryKeyMixin

# Reference values: UNCONFIRMED (shown as "-------------"), APPROVED,
# APPROVED_WITH_REMARKS, REJECTED - see docs/01 and docs/03 section 9.3.
UNCONFIRMED_STATUS_CODE = "UNCONFIRMED"


class InspectionStatus(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "inspection_statuses"

    code: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
    label: Mapped[str] = mapped_column(String(64), nullable=False)
    display_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)


class InspectionReport(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "inspection_reports"

    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    inspection_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    inspection_date_source: Mapped[str | None] = mapped_column(String(32), nullable=True)
    report_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    expiry_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    inspection_status_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("inspection_statuses.id"), nullable=False
    )
    inspection_body_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    certificate_number: Mapped[str | None] = mapped_column(String(128), nullable=True)
    remarks: Mapped[str | None] = mapped_column(String, nullable=True)

    validated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    validated_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)

    document: Mapped["Document"] = relationship()
    inspection_status: Mapped["InspectionStatus"] = relationship()
    findings: Mapped[list["InspectionFinding"]] = relationship(
        back_populates="inspection_report", cascade="all, delete-orphan"
    )


class InspectionFinding(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "inspection_findings"

    inspection_report_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("inspection_reports.id", ondelete="CASCADE"), nullable=False
    )
    finding_number: Mapped[str | None] = mapped_column(String(32), nullable=True)
    severity: Mapped[str] = mapped_column(String(16), nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    arei_reference: Mapped[str | None] = mapped_column(String(64), nullable=True)
    is_resolved: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    resolution_document_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("documents.id", ondelete="SET NULL"), nullable=True
    )

    inspection_report: Mapped["InspectionReport"] = relationship(back_populates="findings")


class InspectionSchedule(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "inspection_schedules"

    site_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("sites.id", ondelete="CASCADE"), nullable=False
    )
    installation_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("installations.id", ondelete="SET NULL"), nullable=True
    )
    discipline_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("disciplines.id"), nullable=False
    )
    next_due_date: Mapped[date] = mapped_column(Date, nullable=False)
    source_report_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("inspection_reports.id", ondelete="SET NULL"), nullable=True
    )
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="OPEN")
    reminder_policy_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)

    site: Mapped["Site"] = relationship()
    discipline: Mapped["Discipline"] = relationship()
