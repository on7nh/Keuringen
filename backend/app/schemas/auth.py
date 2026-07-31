from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    status: str  # STRONG_AUTH_REQUIRED, OK
    challenge_id: uuid.UUID | None = None
    allowed_methods: list[str] = Field(default_factory=list)
    expires_at: datetime | None = None
    access_token: str | None = None
    refresh_token: str | None = None
    token_type: str = "bearer"


class TotpVerifyRequest(BaseModel):
    challenge_id: uuid.UUID
    code: str


class TotpSetupResponse(BaseModel):
    registration_id: uuid.UUID
    secret: str
    otpauth_uri: str
    qr_code_data_uri: str


class TotpConfirmRequest(BaseModel):
    registration_id: uuid.UUID
    code: str


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


class PasskeyRegisterOptionsRequest(BaseModel):
    device_name: str
    authenticator_attachment: str | None = None


class PasskeyRegisterVerifyRequest(BaseModel):
    challenge_id: uuid.UUID
    device_name: str
    credential: dict


class PasskeyLoginOptionsRequest(BaseModel):
    email: EmailStr | None = None


class PasskeyLoginVerifyRequest(BaseModel):
    challenge_id: uuid.UUID
    credential: dict


class PasskeyOut(BaseModel):
    id: uuid.UUID
    device_name: str
    authenticator_attachment: str | None
    registered_at: datetime
    last_used_at: datetime | None

    model_config = {"from_attributes": True}


class PasskeyPatchRequest(BaseModel):
    device_name: str


class RecoveryCodesGenerateResponse(BaseModel):
    codes: list[str]
    generated_at: datetime


class RecoveryCodesStatus(BaseModel):
    remaining_count: int
    generated_at: datetime | None


class RecoveryCodeUseRequest(BaseModel):
    challenge_id: uuid.UUID
    code: str


class StepUpOptionsRequest(BaseModel):
    intended_action: str
    resource_id: uuid.UUID | None = None


class StepUpOptionsResponse(BaseModel):
    step_up_id: uuid.UUID
    allowed_methods: list[str]
    expires_at: datetime


class StepUpVerifyRequest(BaseModel):
    step_up_id: uuid.UUID
    code: str | None = None
    credential: dict | None = None


class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str = Field(min_length=8)


class SessionOut(BaseModel):
    id: uuid.UUID
    device_label: str | None
    ip_address: str | None
    authentication_method: str
    created_at: datetime
    last_seen_at: datetime
    expires_at: datetime

    model_config = {"from_attributes": True}


class MeResponse(BaseModel):
    id: uuid.UUID
    email: str
    display_name: str
    is_system_admin: bool
    organization_roles: list[dict]
    site_roles: list[dict]
