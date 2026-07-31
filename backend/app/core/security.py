from __future__ import annotations

import base64
import hashlib
import secrets
from datetime import datetime, timedelta, timezone

from cryptography.fernet import Fernet
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import get_settings

settings = get_settings()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return pwd_context.verify(password, password_hash)


def _fernet_key() -> bytes:
    raw = settings.totp_encryption_key.encode("utf-8")
    digest = hashlib.sha256(raw).digest()
    return base64.urlsafe_b64encode(digest)


def encrypt_secret(plaintext: str) -> bytes:
    f = Fernet(_fernet_key())
    return f.encrypt(plaintext.encode("utf-8"))


def decrypt_secret(ciphertext: bytes) -> str:
    f = Fernet(_fernet_key())
    return f.decrypt(ciphertext).decode("utf-8")


def hash_lookup_value(value: str | bytes) -> bytes:
    """One-way hash used for indexed lookups (credential IDs, recovery codes)."""
    if isinstance(value, str):
        value = value.encode("utf-8")
    return hashlib.sha256(value).digest()


def generate_recovery_code() -> str:
    raw = secrets.token_hex(5)
    return f"{raw[:5]}-{raw[5:]}".upper()


def create_access_token(subject: str, extra_claims: dict | None = None) -> str:
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=settings.jwt_access_token_minutes)
    payload = {"sub": subject, "type": "access", "iat": now, "exp": expire}
    if extra_claims:
        payload.update(extra_claims)
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def create_refresh_token_value() -> str:
    return secrets.token_urlsafe(48)


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    except JWTError as exc:
        raise ValueError("invalid token") from exc


def is_step_up_valid(step_up_authenticated_at: datetime | None) -> bool:
    if step_up_authenticated_at is None:
        return False
    if step_up_authenticated_at.tzinfo is None:
        step_up_authenticated_at = step_up_authenticated_at.replace(tzinfo=timezone.utc)
    age = datetime.now(timezone.utc) - step_up_authenticated_at
    return age.total_seconds() <= settings.step_up_validity_seconds
