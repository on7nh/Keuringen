from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import (
    ARRAY,
    BigInteger,
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    LargeBinary,
    String,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import INET, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.mixins import UUIDPrimaryKeyMixin


class UserAuthenticationMethod(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "user_authentication_methods"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    method_type: Mapped[str] = mapped_column(String(32), nullable=False)  # PASSKEY, TOTP, RECOVERY_CODES
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="PENDING")
    is_primary: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    registered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    revoked_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    revocation_reason: Mapped[str | None] = mapped_column(String(255), nullable=True)

    user: Mapped["User"] = relationship(back_populates="authentication_methods")


class UserPasskey(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "user_passkeys"
    __table_args__ = (UniqueConstraint("credential_id_hash", name="uq_user_passkeys_credential_hash"),)

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    organization_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="SET NULL"), nullable=True
    )
    authentication_method_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("user_authentication_methods.id", ondelete="CASCADE"), nullable=False
    )

    credential_id: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    credential_id_hash: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    public_key_cose: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    sign_count: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    aaguid: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    transports: Mapped[list[str] | None] = mapped_column(ARRAY(String), nullable=True)
    authenticator_attachment: Mapped[str | None] = mapped_column(String(32), nullable=True)
    credential_type: Mapped[str] = mapped_column(String(32), nullable=False, default="public-key")
    is_discoverable: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    backup_eligible: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    backup_state: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    user_verification_required: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    device_name: Mapped[str] = mapped_column(String(128), nullable=False)

    registered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    last_used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    revoked_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    revocation_reason: Mapped[str | None] = mapped_column(String(255), nullable=True)

    user: Mapped["User"] = relationship(back_populates="passkeys")


class UserTotpConfiguration(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "user_totp_configurations"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    authentication_method_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("user_authentication_methods.id", ondelete="CASCADE"), nullable=False
    )
    secret_encrypted: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    encryption_key_version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    algorithm: Mapped[str] = mapped_column(String(16), nullable=False, default="SHA1")
    digits: Mapped[int] = mapped_column(Integer, nullable=False, default=6)
    period_seconds: Mapped[int] = mapped_column(Integer, nullable=False, default=30)

    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_used_time_step: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    last_used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class RecoveryCodeSet(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "recovery_code_sets"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    authentication_method_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("user_authentication_methods.id", ondelete="CASCADE"), nullable=False
    )
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    generated_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    revoked_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    code_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    remaining_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    codes: Mapped[list["RecoveryCode"]] = relationship(back_populates="code_set", cascade="all, delete-orphan")


class RecoveryCode(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "recovery_codes"

    recovery_code_set_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("recovery_code_sets.id", ondelete="CASCADE"), nullable=False
    )
    code_hash: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    used_ip_address: Mapped[str | None] = mapped_column(INET, nullable=True)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    code_set: Mapped["RecoveryCodeSet"] = relationship(back_populates="codes")


class WebAuthnChallenge(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "webauthn_challenges"

    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=True
    )
    session_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    challenge_hash: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    challenge_value: Mapped[str] = mapped_column(String(255), nullable=False)
    ceremony_type: Mapped[str] = mapped_column(String(16), nullable=False)  # REGISTRATION, AUTHENTICATION, STEP_UP
    rp_id: Mapped[str] = mapped_column(String(255), nullable=False)
    origin: Mapped[str] = mapped_column(String(255), nullable=False)
    intended_action: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    invalidated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class UserSession(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "user_sessions"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    organization_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="SET NULL"), nullable=True
    )
    refresh_token_hash: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    token_family_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    device_label: Mapped[str | None] = mapped_column(String(128), nullable=True)
    ip_address: Mapped[str | None] = mapped_column(INET, nullable=True)
    user_agent: Mapped[str | None] = mapped_column(String(512), nullable=True)
    authentication_method: Mapped[str] = mapped_column(String(32), nullable=False)
    strong_authenticated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    step_up_authenticated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    last_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    revoked_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    revocation_reason: Mapped[str | None] = mapped_column(String(255), nullable=True)


class AuthenticationEvent(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "authentication_events"

    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    organization_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    session_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    event_type: Mapped[str] = mapped_column(String(64), nullable=False)
    method_type: Mapped[str | None] = mapped_column(String(32), nullable=True)
    result: Mapped[str] = mapped_column(String(16), nullable=False)  # SUCCESS, FAILURE, BLOCKED
    failure_reason: Mapped[str | None] = mapped_column(String(255), nullable=True)
    credential_reference_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    ip_address: Mapped[str | None] = mapped_column(INET, nullable=True)
    user_agent: Mapped[str | None] = mapped_column(String(512), nullable=True)
    correlation_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class OrganizationAuthenticationPolicy(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "organization_authentication_policies"

    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    strong_authentication_required: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    required_for_all_users: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    allow_totp: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    allow_passkeys: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    allow_passwordless: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    allow_usernameless_login: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    require_user_verification: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    minimum_active_methods: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    step_up_validity_seconds: Mapped[int] = mapped_column(Integer, nullable=False, default=300)
    session_max_age_seconds: Mapped[int] = mapped_column(Integer, nullable=False, default=60 * 60 * 12)
    idle_timeout_seconds: Mapped[int] = mapped_column(Integer, nullable=False, default=60 * 60)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
