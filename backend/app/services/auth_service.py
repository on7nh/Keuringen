from __future__ import annotations

import base64
import uuid
from datetime import datetime, timedelta, timezone

import pyotp
import qrcode
import qrcode.image.svg
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from webauthn import (
    generate_authentication_options,
    generate_registration_options,
    options_to_json,
    verify_authentication_response,
    verify_registration_response,
)
from webauthn.helpers.structs import (
    AuthenticatorSelectionCriteria,
    PublicKeyCredentialDescriptor,
    UserVerificationRequirement,
)

from app.core.config import get_settings
from app.core.security import (
    create_access_token,
    create_refresh_token_value,
    decrypt_secret,
    encrypt_secret,
    generate_recovery_code,
    hash_lookup_value,
    hash_password,
    verify_password,
)
from app.models.auth import (
    AuthenticationEvent,
    RecoveryCode,
    RecoveryCodeSet,
    UserAuthenticationMethod,
    UserPasskey,
    UserSession,
    UserTotpConfiguration,
    WebAuthnChallenge,
)
from app.models.user import User

settings = get_settings()

STRONG_METHOD_TYPES = ("PASSKEY", "TOTP")


def now() -> datetime:
    return datetime.now(timezone.utc)


_now = now  # internal alias used throughout this module


def _active_strong_methods(db: Session, user: User) -> list[UserAuthenticationMethod]:
    return (
        db.query(UserAuthenticationMethod)
        .filter(
            UserAuthenticationMethod.user_id == user.id,
            UserAuthenticationMethod.status == "ACTIVE",
            UserAuthenticationMethod.method_type.in_(STRONG_METHOD_TYPES),
        )
        .all()
    )


def record_authentication_event(
    db: Session,
    *,
    user: User | None,
    event_type: str,
    result: str,
    method_type: str | None = None,
    failure_reason: str | None = None,
    correlation_id: uuid.UUID | None = None,
) -> None:
    db.add(
        AuthenticationEvent(
            user_id=user.id if user else None,
            event_type=event_type,
            method_type=method_type,
            result=result,
            failure_reason=failure_reason,
            correlation_id=correlation_id or uuid.uuid4(),
            created_at=_now(),
        )
    )


def authenticate_password(db: Session, email: str, password: str) -> User:
    user = db.query(User).filter(User.email == email, User.deleted_at.is_(None)).first()
    if user is None or user.password_hash is None:
        record_authentication_event(db, user=None, event_type="LOGIN", result="FAILURE")
        db.commit()
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="AUTHENTICATION_FAILED")

    if user.locked_until and user.locked_until > _now():
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="ACCOUNT_LOCKED")

    if not verify_password(password, user.password_hash):
        user.failed_login_count += 1
        if user.failed_login_count >= 10:
            user.locked_until = _now() + timedelta(minutes=15)
        record_authentication_event(db, user=user, event_type="LOGIN", result="FAILURE")
        db.commit()
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="AUTHENTICATION_FAILED")

    user.failed_login_count = 0
    db.commit()
    return user


def strong_auth_required(user: User) -> bool:
    return user.is_system_admin or user.strong_authentication_required


def build_step_up_challenge_response(db: Session, user: User) -> dict:
    strong_methods = _active_strong_methods(db, user)
    allowed = sorted({m.method_type for m in strong_methods})
    challenge = WebAuthnChallenge(
        user_id=user.id,
        challenge_hash=b"",
        challenge_value="",
        ceremony_type="AUTHENTICATION",
        rp_id=settings.webauthn_rp_id,
        origin=settings.webauthn_origin,
        created_at=_now(),
        expires_at=_now() + timedelta(seconds=settings.webauthn_challenge_ttl_seconds),
    )
    db.add(challenge)
    db.flush()
    return {
        "status": "STRONG_AUTH_REQUIRED",
        "challenge_id": challenge.id,
        "allowed_methods": allowed,
        "expires_at": challenge.expires_at,
    }


def issue_session_and_tokens(
    db: Session,
    user: User,
    *,
    authentication_method: str,
    strong_authenticated: bool,
    ip_address: str | None = None,
    user_agent: str | None = None,
    device_label: str | None = None,
) -> tuple[str, str]:
    refresh_token = create_refresh_token_value()
    session = UserSession(
        user_id=user.id,
        refresh_token_hash=hash_lookup_value(refresh_token),
        token_family_id=uuid.uuid4(),
        device_label=device_label,
        ip_address=ip_address,
        user_agent=user_agent,
        authentication_method=authentication_method,
        strong_authenticated_at=_now() if strong_authenticated else None,
        created_at=_now(),
        last_seen_at=_now(),
        expires_at=_now() + timedelta(days=settings.jwt_refresh_token_days),
    )
    db.add(session)
    db.flush()

    user.last_login_at = _now()

    access_token = create_access_token(str(user.id), {"session_id": str(session.id)})
    record_authentication_event(
        db, user=user, event_type="LOGIN", result="SUCCESS", method_type=authentication_method
    )
    db.commit()
    return access_token, refresh_token


def refresh_session(db: Session, refresh_token: str) -> tuple[str, str]:
    token_hash = hash_lookup_value(refresh_token)
    session = (
        db.query(UserSession)
        .filter(UserSession.refresh_token_hash == token_hash, UserSession.revoked_at.is_(None))
        .first()
    )
    if session is None or session.expires_at < _now():
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="SESSION_REVOKED")

    user = db.get(User, session.user_id)
    if user is None or not user.is_active:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Account is not active")

    new_refresh = create_refresh_token_value()
    session.refresh_token_hash = hash_lookup_value(new_refresh)
    session.last_seen_at = _now()
    db.flush()

    access_token = create_access_token(str(user.id), {"session_id": str(session.id)})
    db.commit()
    return access_token, new_refresh


def revoke_session(db: Session, session: UserSession, *, reason: str = "LOGOUT") -> None:
    session.revoked_at = _now()
    session.revocation_reason = reason
    db.commit()


# --- TOTP ---------------------------------------------------------------


def setup_totp(db: Session, user: User) -> tuple[uuid.UUID, str, str]:
    secret = pyotp.random_base32()
    method = UserAuthenticationMethod(
        user_id=user.id, method_type="TOTP", status="PENDING", registered_at=_now()
    )
    db.add(method)
    db.flush()

    db.add(
        UserTotpConfiguration(
            user_id=user.id,
            authentication_method_id=method.id,
            secret_encrypted=encrypt_secret(secret),
        )
    )
    db.commit()

    otpauth_uri = pyotp.totp.TOTP(secret).provisioning_uri(
        name=user.email, issuer_name=settings.totp_issuer
    )
    return method.id, secret, otpauth_uri


def totp_qr_data_uri(otpauth_uri: str) -> str:
    factory = qrcode.image.svg.SvgImage
    img = qrcode.make(otpauth_uri, image_factory=factory)
    import io

    buf = io.BytesIO()
    img.save(buf)
    encoded = base64.b64encode(buf.getvalue()).decode("ascii")
    return f"data:image/svg+xml;base64,{encoded}"


def _totp_config_for_method(db: Session, registration_id: uuid.UUID) -> UserTotpConfiguration:
    config = (
        db.query(UserTotpConfiguration)
        .filter(UserTotpConfiguration.authentication_method_id == registration_id)
        .first()
    )
    if config is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="TOTP registration not found")
    return config


def confirm_totp(db: Session, user: User, registration_id: uuid.UUID, code: str) -> None:
    config = _totp_config_for_method(db, registration_id)
    secret = decrypt_secret(config.secret_encrypted)
    totp = pyotp.TOTP(secret)
    time_step = int(_now().timestamp() // config.period_seconds)

    if not totp.verify(code, valid_window=1) or config.last_used_time_step == time_step:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="TOTP_INVALID")

    config.verified_at = _now()
    config.last_used_time_step = time_step
    config.last_used_at = _now()

    method = db.get(UserAuthenticationMethod, registration_id)
    method.status = "ACTIVE"
    method.verified_at = _now()
    record_authentication_event(db, user=user, event_type="TOTP_ENABLED", result="SUCCESS")
    db.commit()


def verify_totp_code(db: Session, user: User, code: str) -> bool:
    config = (
        db.query(UserTotpConfiguration)
        .join(
            UserAuthenticationMethod,
            UserAuthenticationMethod.id == UserTotpConfiguration.authentication_method_id,
        )
        .filter(
            UserTotpConfiguration.user_id == user.id,
            UserAuthenticationMethod.status == "ACTIVE",
        )
        .first()
    )
    if config is None:
        return False

    secret = decrypt_secret(config.secret_encrypted)
    totp = pyotp.TOTP(secret)
    time_step = int(_now().timestamp() // config.period_seconds)

    if config.last_used_time_step == time_step:
        return False  # reject reuse within the same time window

    if not totp.verify(code, valid_window=1):
        return False

    config.last_used_time_step = time_step
    config.last_used_at = _now()
    db.commit()
    return True


def revoke_totp(db: Session, user: User) -> None:
    _ensure_not_last_method(db, user, excluding_method_type="TOTP")
    config = (
        db.query(UserTotpConfiguration)
        .join(
            UserAuthenticationMethod,
            UserAuthenticationMethod.id == UserTotpConfiguration.authentication_method_id,
        )
        .filter(
            UserTotpConfiguration.user_id == user.id,
            UserAuthenticationMethod.status == "ACTIVE",
        )
        .first()
    )
    if config is None:
        return
    config.revoked_at = _now()
    method = db.get(UserAuthenticationMethod, config.authentication_method_id)
    method.status = "REVOKED"
    method.revoked_at = _now()
    method.revoked_by = user.id
    record_authentication_event(db, user=user, event_type="TOTP_REVOKED", result="SUCCESS")
    db.commit()


def _ensure_not_last_method(
    db: Session, user: User, *, excluding_method_type: str, excluding_method_id: uuid.UUID | None = None
) -> None:
    """Blocks removing the last usable strong authentication method,
    per docs/01 and docs/03 constraint LAST_AUTHENTICATION_METHOD."""
    remaining = [
        m
        for m in _active_strong_methods(db, user)
        if not (
            m.method_type == excluding_method_type
            and (excluding_method_id is None or m.id == excluding_method_id)
        )
    ]
    if not remaining:
        raise HTTPException(status.HTTP_409_CONFLICT, detail="LAST_AUTHENTICATION_METHOD")


# --- Recovery codes -------------------------------------------------------


def generate_recovery_codes(db: Session, user: User) -> list[str]:
    method = (
        db.query(UserAuthenticationMethod)
        .filter(
            UserAuthenticationMethod.user_id == user.id,
            UserAuthenticationMethod.method_type == "RECOVERY_CODES",
        )
        .first()
    )
    if method is None:
        method = UserAuthenticationMethod(
            user_id=user.id, method_type="RECOVERY_CODES", status="ACTIVE", registered_at=_now()
        )
        db.add(method)
        db.flush()

    # Invalidate previous active sets - a new set makes all previous ones invalid.
    db.query(RecoveryCodeSet).filter(
        RecoveryCodeSet.user_id == user.id, RecoveryCodeSet.revoked_at.is_(None)
    ).update({"revoked_at": _now(), "revoked_by": user.id})

    codes = [generate_recovery_code() for _ in range(10)]
    code_set = RecoveryCodeSet(
        user_id=user.id,
        authentication_method_id=method.id,
        generated_at=_now(),
        generated_by=user.id,
        code_count=len(codes),
        remaining_count=len(codes),
    )
    db.add(code_set)
    db.flush()

    for code in codes:
        db.add(RecoveryCode(recovery_code_set_id=code_set.id, code_hash=hash_lookup_value(code)))

    record_authentication_event(db, user=user, event_type="RECOVERY_CODES_GENERATED", result="SUCCESS")
    db.commit()
    return codes


def use_recovery_code(db: Session, user: User, code: str) -> bool:
    code_hash = hash_lookup_value(code.strip().upper())
    recovery_code = (
        db.query(RecoveryCode)
        .join(RecoveryCodeSet, RecoveryCodeSet.id == RecoveryCode.recovery_code_set_id)
        .filter(
            RecoveryCodeSet.user_id == user.id,
            RecoveryCodeSet.revoked_at.is_(None),
            RecoveryCode.code_hash == code_hash,
            RecoveryCode.used_at.is_(None),
            RecoveryCode.revoked_at.is_(None),
        )
        .first()
    )
    if recovery_code is None:
        record_authentication_event(
            db, user=user, event_type="RECOVERY_CODE_USED", result="FAILURE"
        )
        db.commit()
        return False

    recovery_code.used_at = _now()
    code_set = db.get(RecoveryCodeSet, recovery_code.recovery_code_set_id)
    code_set.remaining_count = max(0, code_set.remaining_count - 1)
    record_authentication_event(db, user=user, event_type="RECOVERY_CODE_USED", result="SUCCESS")
    db.commit()
    return True


# --- WebAuthn / Passkeys ---------------------------------------------------


def build_registration_options(db: Session, user: User, device_name: str, attachment: str | None) -> dict:
    existing_credentials = [
        PublicKeyCredentialDescriptor(id=pk.credential_id)
        for pk in db.query(UserPasskey).filter(
            UserPasskey.user_id == user.id, UserPasskey.revoked_at.is_(None)
        )
    ]

    authenticator_selection = None
    if attachment:
        authenticator_selection = AuthenticatorSelectionCriteria(authenticator_attachment=attachment)

    options = generate_registration_options(
        rp_id=settings.webauthn_rp_id,
        rp_name=settings.webauthn_rp_name,
        user_id=str(user.id).encode("utf-8"),
        user_name=user.email,
        user_display_name=user.display_name,
        exclude_credentials=existing_credentials,
        authenticator_selection=authenticator_selection,
    )

    challenge = WebAuthnChallenge(
        user_id=user.id,
        challenge_hash=hash_lookup_value(options.challenge),
        challenge_value=base64.urlsafe_b64encode(options.challenge).decode(),
        ceremony_type="REGISTRATION",
        rp_id=settings.webauthn_rp_id,
        origin=settings.webauthn_origin,
        intended_action=device_name,
        created_at=_now(),
        expires_at=_now() + timedelta(seconds=settings.webauthn_challenge_ttl_seconds),
    )
    db.add(challenge)
    db.commit()

    return {"challenge_id": str(challenge.id), "options": options_to_json(options)}


def _consume_challenge(db: Session, challenge_id: uuid.UUID, ceremony_type: str) -> WebAuthnChallenge:
    challenge = db.get(WebAuthnChallenge, challenge_id)
    if challenge is None or challenge.ceremony_type != ceremony_type:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="WEBAUTHN_CHALLENGE_EXPIRED")
    if challenge.used_at is not None or challenge.invalidated_at is not None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="WEBAUTHN_CHALLENGE_USED")
    if challenge.expires_at < _now():
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="WEBAUTHN_CHALLENGE_EXPIRED")
    challenge.used_at = _now()
    return challenge


def verify_registration(db: Session, user: User, challenge_id: uuid.UUID, device_name: str, credential: dict) -> UserPasskey:
    challenge = _consume_challenge(db, challenge_id, "REGISTRATION")
    expected_challenge = base64.urlsafe_b64decode(challenge.challenge_value)

    try:
        verification = verify_registration_response(
            credential=credential,
            expected_challenge=expected_challenge,
            expected_rp_id=settings.webauthn_rp_id,
            expected_origin=settings.webauthn_origin,
        )
    except Exception as exc:
        record_authentication_event(
            db, user=user, event_type="PASSKEY_REGISTERED", result="FAILURE", failure_reason=str(exc)
        )
        db.commit()
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="WEBAUTHN_SIGNATURE_INVALID") from exc

    method = UserAuthenticationMethod(
        user_id=user.id, method_type="PASSKEY", status="ACTIVE", registered_at=_now(), verified_at=_now()
    )
    db.add(method)
    db.flush()

    passkey = UserPasskey(
        user_id=user.id,
        authentication_method_id=method.id,
        credential_id=verification.credential_id,
        credential_id_hash=hash_lookup_value(verification.credential_id),
        public_key_cose=verification.credential_public_key,
        sign_count=verification.sign_count,
        credential_type="public-key",
        is_discoverable=bool(verification.credential_device_type == "multi_device"),
        backup_eligible=verification.credential_backed_up,
        device_name=device_name,
        registered_at=_now(),
    )
    db.add(passkey)
    record_authentication_event(db, user=user, event_type="PASSKEY_REGISTERED", result="SUCCESS")
    db.commit()
    db.refresh(passkey)
    return passkey


def build_authentication_options(db: Session, user: User | None) -> dict:
    allow_credentials = None
    if user is not None:
        allow_credentials = [
            PublicKeyCredentialDescriptor(id=pk.credential_id)
            for pk in db.query(UserPasskey).filter(
                UserPasskey.user_id == user.id, UserPasskey.revoked_at.is_(None)
            )
        ]

    options = generate_authentication_options(
        rp_id=settings.webauthn_rp_id,
        allow_credentials=allow_credentials,
        user_verification=UserVerificationRequirement.PREFERRED,
    )

    challenge = WebAuthnChallenge(
        user_id=user.id if user else None,
        challenge_hash=hash_lookup_value(options.challenge),
        challenge_value=base64.urlsafe_b64encode(options.challenge).decode(),
        ceremony_type="AUTHENTICATION",
        rp_id=settings.webauthn_rp_id,
        origin=settings.webauthn_origin,
        created_at=_now(),
        expires_at=_now() + timedelta(seconds=settings.webauthn_challenge_ttl_seconds),
    )
    db.add(challenge)
    db.commit()
    return {"challenge_id": str(challenge.id), "options": options_to_json(options)}


def verify_authentication(db: Session, challenge_id: uuid.UUID, credential: dict) -> User:
    challenge = _consume_challenge(db, challenge_id, "AUTHENTICATION")
    expected_challenge = base64.urlsafe_b64decode(challenge.challenge_value)

    raw_id = credential.get("rawId") or credential.get("id")
    credential_id_hash = hash_lookup_value(base64.urlsafe_b64decode(raw_id + "=="))
    passkey = (
        db.query(UserPasskey)
        .filter(UserPasskey.credential_id_hash == credential_id_hash, UserPasskey.revoked_at.is_(None))
        .first()
    )
    if passkey is None:
        db.commit()
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="PASSKEY_REVOKED")

    try:
        verification = verify_authentication_response(
            credential=credential,
            expected_challenge=expected_challenge,
            expected_rp_id=settings.webauthn_rp_id,
            expected_origin=settings.webauthn_origin,
            credential_public_key=passkey.public_key_cose,
            credential_current_sign_count=passkey.sign_count,
        )
    except Exception as exc:
        record_authentication_event(
            db, user=None, event_type="LOGIN", result="FAILURE", method_type="PASSKEY", failure_reason=str(exc)
        )
        db.commit()
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="WEBAUTHN_SIGNATURE_INVALID") from exc

    passkey.sign_count = verification.new_sign_count
    passkey.last_used_at = _now()

    method = db.get(UserAuthenticationMethod, passkey.authentication_method_id)
    method.last_used_at = _now()

    user = db.get(User, passkey.user_id)
    record_authentication_event(db, user=user, event_type="LOGIN", result="SUCCESS", method_type="PASSKEY")
    db.commit()
    return user


def revoke_passkey(db: Session, user: User, passkey_id: uuid.UUID, reason: str = "USER_REQUEST") -> None:
    passkey = db.get(UserPasskey, passkey_id)
    if passkey is None or passkey.user_id != user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Passkey not found")
    if passkey.revoked_at is not None:
        return

    _ensure_not_last_method(db, user, excluding_method_type="PASSKEY", excluding_method_id=passkey.authentication_method_id)

    passkey.revoked_at = _now()
    passkey.revoked_by = user.id
    passkey.revocation_reason = reason

    method = db.get(UserAuthenticationMethod, passkey.authentication_method_id)
    method.status = "REVOKED"
    method.revoked_at = _now()
    method.revoked_by = user.id

    record_authentication_event(db, user=user, event_type="PASSKEY_REVOKED", result="SUCCESS")
    db.commit()
