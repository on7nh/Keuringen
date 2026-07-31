from __future__ import annotations

import uuid
from datetime import date

from sqlalchemy import Boolean, Date, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.mixins import BusinessEntityMixin, UUIDPrimaryKeyMixin


class Organization(Base, BusinessEntityMixin):
    __tablename__ = "organizations"

    code: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    sharepoint_marking_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    default_timezone: Mapped[str] = mapped_column(String(64), nullable=False, default="Europe/Brussels")

    sites: Mapped[list["Site"]] = relationship(back_populates="organization")
    user_roles: Mapped[list["UserOrganizationRole"]] = relationship(back_populates="organization")


class Site(Base, BusinessEntityMixin):
    __tablename__ = "sites"
    __table_args__ = (
        UniqueConstraint("organization_id", "site_number", name="uq_sites_organization_site_number"),
        UniqueConstraint("organization_id", "code", name="uq_sites_organization_code"),
    )

    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    site_number: Mapped[str] = mapped_column(String(32), nullable=False)
    code: Mapped[str] = mapped_column(String(64), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)

    storage_code: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
    storage_relative_path: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)

    is_temporary_site_number: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    address_street: Mapped[str | None] = mapped_column(String(255), nullable=True)
    address_number: Mapped[str | None] = mapped_column(String(32), nullable=True)
    address_postal_code: Mapped[str | None] = mapped_column(String(32), nullable=True)
    address_city: Mapped[str | None] = mapped_column(String(255), nullable=True)
    address_country: Mapped[str | None] = mapped_column(String(2), nullable=True)

    timezone: Mapped[str] = mapped_column(String(64), nullable=False, default="Europe/Brussels")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    organization: Mapped["Organization"] = relationship(back_populates="sites")
    installations: Mapped[list["Installation"]] = relationship(back_populates="site")
    user_roles: Mapped[list["UserSiteRole"]] = relationship(back_populates="site")


class InstallationType(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "installation_types"

    code: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


class Installation(Base, BusinessEntityMixin):
    __tablename__ = "installations"

    site_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("sites.id", ondelete="CASCADE"), nullable=False
    )
    installation_type_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("installation_types.id"), nullable=False
    )
    code: Mapped[str] = mapped_column(String(64), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    ean_number: Mapped[str | None] = mapped_column(String(32), nullable=True)
    commissioned_on: Mapped[date | None] = mapped_column(Date, nullable=True)
    decommissioned_on: Mapped[date | None] = mapped_column(Date, nullable=True)
    installation_metadata: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    site: Mapped["Site"] = relationship(back_populates="installations")
    installation_type: Mapped["InstallationType"] = relationship()


class Discipline(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "disciplines"

    code: Mapped[str] = mapped_column(String(16), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    validity_value: Mapped[int | None] = mapped_column(Integer, nullable=True)
    validity_unit: Mapped[str | None] = mapped_column(String(8), nullable=True)  # day, month, year
    is_general: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
