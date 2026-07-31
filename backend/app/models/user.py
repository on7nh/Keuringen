from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import CITEXT, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.mixins import BusinessEntityMixin


class User(Base, BusinessEntityMixin):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(CITEXT, unique=True, nullable=False, index=True)
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)

    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    is_system_admin: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    preferred_authentication_method: Mapped[str | None] = mapped_column(String(32), nullable=True)
    strong_authentication_required: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )
    passwordless_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    failed_login_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    locked_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    credentials_changed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    organization_roles: Mapped[list["UserOrganizationRole"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    site_roles: Mapped[list["UserSiteRole"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    authentication_methods: Mapped[list["UserAuthenticationMethod"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    passkeys: Mapped[list["UserPasskey"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
