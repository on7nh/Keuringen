from __future__ import annotations

import uuid
from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, Numeric, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.mixins import BusinessEntityMixin, UUIDPrimaryKeyMixin


class DocumentType(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "document_types"

    code: Mapped[str] = mapped_column(String(16), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    requires_inspection_data: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    supports_ai_analysis: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


class Document(Base, BusinessEntityMixin):
    __tablename__ = "documents"

    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    site_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("sites.id", ondelete="CASCADE"), nullable=False
    )
    installation_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("installations.id", ondelete="SET NULL"), nullable=True
    )
    discipline_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("disciplines.id"), nullable=False
    )
    document_type_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("document_types.id"), nullable=False
    )
    current_version_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("document_versions.id", ondelete="SET NULL", use_alter=True),
        nullable=True,
    )

    title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    document_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    document_date_source: Mapped[str | None] = mapped_column(String(32), nullable=True)

    ai_status: Mapped[str] = mapped_column(String(32), nullable=False, default="PENDING")
    validation_status: Mapped[str] = mapped_column(String(32), nullable=False, default="PENDING")

    sharepoint_marked: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    sharepoint_marked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    sharepoint_marked_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)

    retention_until: Mapped[date | None] = mapped_column(Date, nullable=True)

    validated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    validated_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)

    site: Mapped["Site"] = relationship()
    discipline: Mapped["Discipline"] = relationship()
    document_type: Mapped["DocumentType"] = relationship()
    versions: Mapped[list["DocumentVersion"]] = relationship(
        back_populates="document",
        cascade="all, delete-orphan",
        foreign_keys="DocumentVersion.document_id",
    )
    fields: Mapped[list["DocumentField"]] = relationship(
        back_populates="document", cascade="all, delete-orphan"
    )
    current_version: Mapped["DocumentVersion | None"] = relationship(
        foreign_keys=[current_version_id], post_update=True
    )


class DocumentVersion(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "document_versions"
    __table_args__ = (
        UniqueConstraint("document_id", "version_number", name="uq_document_versions_document_version"),
    )

    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False
    )
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    storage_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    stored_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_hash_sha256: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    file_size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    mime_type: Mapped[str] = mapped_column(String(128), nullable=False)
    file_extension: Mapped[str] = mapped_column(String(16), nullable=False)

    uploaded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    uploaded_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)

    technical_metadata: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    is_quarantined: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    malware_scan_status: Mapped[str] = mapped_column(String(16), nullable=False, default="PENDING")

    document: Mapped["Document"] = relationship(
        back_populates="versions", foreign_keys=[document_id]
    )


class DocumentField(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "document_fields"

    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False
    )
    field_code: Mapped[str] = mapped_column(String(64), nullable=False)
    value_text: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    value_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    value_numeric: Mapped[float | None] = mapped_column(Numeric, nullable=True)
    value_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    source_type: Mapped[str] = mapped_column(String(32), nullable=False)
    is_confirmed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    confirmed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    confirmed_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)

    document: Mapped["Document"] = relationship(back_populates="fields")


class DocumentLink(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "document_links"

    source_document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False
    )
    target_document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False
    )
    link_type: Mapped[str] = mapped_column(String(32), nullable=False)
