from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_session, get_current_user, require_step_up
from app.core.database import get_db
from app.core.security import hash_password, verify_password
from app.models.auth import RecoveryCodeSet, UserPasskey, UserSession, WebAuthnChallenge
from app.models.user import User
from app.schemas.auth import (
    LoginRequest,
    LoginResponse,
    MeResponse,
    PasskeyLoginOptionsRequest,
    PasskeyLoginVerifyRequest,
    PasskeyOut,
    PasskeyPatchRequest,
    PasskeyRegisterOptionsRequest,
    PasskeyRegisterVerifyRequest,
    PasswordChangeRequest,
    RecoveryCodesGenerateResponse,
    RecoveryCodesStatus,
    RecoveryCodeUseRequest,
    RefreshRequest,
    SessionOut,
    StepUpOptionsRequest,
    StepUpOptionsResponse,
    StepUpVerifyRequest,
    TokenPair,
    TotpConfirmRequest,
    TotpSetupResponse,
    TotpVerifyRequest,
)
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest, request: Request, db: Session = Depends(get_db)):
    user = auth_service.authenticate_password(db, payload.email, payload.password)

    if auth_service.strong_auth_required(user):
        challenge = auth_service.build_step_up_challenge_response(db, user)
        db.commit()
        return LoginResponse(**challenge)

    access_token, refresh_token = auth_service.issue_session_and_tokens(
        db,
        user,
        authentication_method="PASSWORD",
        strong_authenticated=False,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    return LoginResponse(status="OK", access_token=access_token, refresh_token=refresh_token)


@router.post("/totp/verify", response_model=LoginResponse)
def totp_login_verify(payload: TotpVerifyRequest, request: Request, db: Session = Depends(get_db)):
    challenge = db.get(WebAuthnChallenge, payload.challenge_id)
    if challenge is None or challenge.user_id is None or challenge.used_at is not None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="WEBAUTHN_CHALLENGE_EXPIRED")

    user = db.get(User, challenge.user_id)
    if not auth_service.verify_totp_code(db, user, payload.code):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="TOTP_INVALID")

    challenge.used_at = auth_service.now()
    access_token, refresh_token = auth_service.issue_session_and_tokens(
        db,
        user,
        authentication_method="TOTP",
        strong_authenticated=True,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    return LoginResponse(status="OK", access_token=access_token, refresh_token=refresh_token)


@router.post("/totp/setup", response_model=TotpSetupResponse, dependencies=[Depends(require_step_up("TOTP_SETUP"))])
def totp_setup(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    registration_id, secret, otpauth_uri = auth_service.setup_totp(db, user)
    return TotpSetupResponse(
        registration_id=registration_id,
        secret=secret,
        otpauth_uri=otpauth_uri,
        qr_code_data_uri=auth_service.totp_qr_data_uri(otpauth_uri),
    )


@router.post("/totp/confirm", status_code=status.HTTP_204_NO_CONTENT)
def totp_confirm(payload: TotpConfirmRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    auth_service.confirm_totp(db, user, payload.registration_id, payload.code)


@router.delete("/totp", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_step_up("TOTP_REVOKE"))])
def totp_revoke(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    auth_service.revoke_totp(db, user)


@router.post("/passkey/register/options", dependencies=[Depends(require_step_up("PASSKEY_REGISTER"))])
def passkey_register_options(
    payload: PasskeyRegisterOptionsRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return auth_service.build_registration_options(
        db, user, payload.device_name, payload.authenticator_attachment
    )


@router.post("/passkey/register/verify", response_model=PasskeyOut)
def passkey_register_verify(
    payload: PasskeyRegisterVerifyRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    passkey = auth_service.verify_registration(
        db, user, payload.challenge_id, payload.device_name, payload.credential
    )
    return passkey


@router.post("/passkey/login/options")
def passkey_login_options(payload: PasskeyLoginOptionsRequest, db: Session = Depends(get_db)):
    user = None
    if payload.email:
        user = db.query(User).filter(User.email == payload.email, User.deleted_at.is_(None)).first()
    return auth_service.build_authentication_options(db, user)


@router.post("/passkey/login/verify", response_model=LoginResponse)
def passkey_login_verify(payload: PasskeyLoginVerifyRequest, request: Request, db: Session = Depends(get_db)):
    user = auth_service.verify_authentication(db, payload.challenge_id, payload.credential)
    access_token, refresh_token = auth_service.issue_session_and_tokens(
        db,
        user,
        authentication_method="PASSKEY",
        strong_authenticated=True,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    return LoginResponse(status="OK", access_token=access_token, refresh_token=refresh_token)


@router.get("/passkey/list", response_model=list[PasskeyOut])
def passkey_list(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return (
        db.query(UserPasskey)
        .filter(UserPasskey.user_id == user.id, UserPasskey.revoked_at.is_(None))
        .all()
    )


@router.patch("/passkey/{passkey_id}", response_model=PasskeyOut)
def passkey_patch(
    passkey_id: uuid.UUID,
    payload: PasskeyPatchRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    passkey = db.get(UserPasskey, passkey_id)
    if passkey is None or passkey.user_id != user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Passkey not found")
    passkey.device_name = payload.device_name
    db.commit()
    db.refresh(passkey)
    return passkey


@router.delete(
    "/passkey/{passkey_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_step_up("PASSKEY_REVOKE"))],
)
def passkey_delete(passkey_id: uuid.UUID, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    auth_service.revoke_passkey(db, user, passkey_id)


@router.post("/recovery-codes/generate", response_model=RecoveryCodesGenerateResponse, dependencies=[Depends(require_step_up("RECOVERY_CODES_GENERATE"))])
def recovery_codes_generate(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    codes = auth_service.generate_recovery_codes(db, user)
    return RecoveryCodesGenerateResponse(codes=codes, generated_at=auth_service.now())


@router.get("/recovery-codes/status", response_model=RecoveryCodesStatus)
def recovery_codes_status(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    code_set = (
        db.query(RecoveryCodeSet)
        .filter(RecoveryCodeSet.user_id == user.id, RecoveryCodeSet.revoked_at.is_(None))
        .order_by(RecoveryCodeSet.generated_at.desc())
        .first()
    )
    if code_set is None:
        return RecoveryCodesStatus(remaining_count=0, generated_at=None)
    return RecoveryCodesStatus(remaining_count=code_set.remaining_count, generated_at=code_set.generated_at)


@router.post("/recovery-code/use", response_model=LoginResponse)
def recovery_code_use(payload: RecoveryCodeUseRequest, request: Request, db: Session = Depends(get_db)):
    challenge = db.get(WebAuthnChallenge, payload.challenge_id)
    if challenge is None or challenge.user_id is None or challenge.used_at is not None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="WEBAUTHN_CHALLENGE_EXPIRED")
    user = db.get(User, challenge.user_id)

    if not auth_service.use_recovery_code(db, user, payload.code):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="RECOVERY_CODE_INVALID")

    challenge.used_at = auth_service.now()
    access_token, refresh_token = auth_service.issue_session_and_tokens(
        db,
        user,
        authentication_method="RECOVERY_CODE",
        strong_authenticated=True,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    return LoginResponse(status="OK", access_token=access_token, refresh_token=refresh_token)


@router.post("/step-up/options", response_model=StepUpOptionsResponse)
def step_up_options(payload: StepUpOptionsRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    challenge = auth_service.build_step_up_challenge_response(db, user)
    db.commit()
    return StepUpOptionsResponse(
        step_up_id=challenge["challenge_id"],
        allowed_methods=challenge["allowed_methods"],
        expires_at=challenge["expires_at"],
    )


@router.post("/step-up/totp/verify", status_code=status.HTTP_204_NO_CONTENT)
def step_up_totp_verify(
    payload: StepUpVerifyRequest,
    user: User = Depends(get_current_user),
    session: UserSession | None = Depends(get_current_session),
    db: Session = Depends(get_db),
):
    if payload.code is None or not auth_service.verify_totp_code(db, user, payload.code):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="TOTP_INVALID")
    if session is not None:
        session.step_up_authenticated_at = auth_service.now()
        db.commit()


@router.post("/step-up/passkey/verify", status_code=status.HTTP_204_NO_CONTENT)
def step_up_passkey_verify(
    payload: StepUpVerifyRequest,
    session: UserSession | None = Depends(get_current_session),
    db: Session = Depends(get_db),
):
    if payload.credential is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="WEBAUTHN_SIGNATURE_INVALID")
    auth_service.verify_authentication(db, payload.step_up_id, payload.credential)
    if session is not None:
        session.step_up_authenticated_at = auth_service.now()
        db.commit()


@router.post("/refresh", response_model=TokenPair)
def refresh(payload: RefreshRequest, db: Session = Depends(get_db)):
    access_token, refresh_token = auth_service.refresh_session(db, payload.refresh_token)
    return TokenPair(access_token=access_token, refresh_token=refresh_token)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(session: UserSession | None = Depends(get_current_session), db: Session = Depends(get_db)):
    if session is not None:
        auth_service.revoke_session(db, session, reason="LOGOUT")


@router.post("/logout-all", status_code=status.HTTP_204_NO_CONTENT)
def logout_all(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    sessions = db.query(UserSession).filter(UserSession.user_id == user.id, UserSession.revoked_at.is_(None)).all()
    for s in sessions:
        s.revoked_at = auth_service.now()
        s.revocation_reason = "LOGOUT_ALL"
    db.commit()


@router.get("/sessions", response_model=list[SessionOut])
def list_sessions(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return (
        db.query(UserSession)
        .filter(UserSession.user_id == user.id, UserSession.revoked_at.is_(None))
        .order_by(UserSession.last_seen_at.desc())
        .all()
    )


@router.delete("/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_step_up("SESSION_REVOKE"))])
def revoke_session_by_id(session_id: uuid.UUID, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    session = db.get(UserSession, session_id)
    if session is None or session.user_id != user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Session not found")
    auth_service.revoke_session(db, session, reason="USER_REQUEST")


@router.post("/password/change", status_code=status.HTTP_204_NO_CONTENT)
def change_password(payload: PasswordChangeRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if user.password_hash is None or not verify_password(payload.current_password, user.password_hash):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="AUTHENTICATION_FAILED")
    user.password_hash = hash_password(payload.new_password)
    user.credentials_changed_at = auth_service.now()
    db.commit()


@router.get("/me", response_model=MeResponse)
def me(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return MeResponse(
        id=user.id,
        email=user.email,
        display_name=user.display_name,
        is_system_admin=user.is_system_admin,
        organization_roles=[
            {"organization_id": str(r.organization_id), "role_id": str(r.role_id)}
            for r in user.organization_roles
        ],
        site_roles=[{"site_id": str(r.site_id), "role_id": str(r.role_id)} for r in user.site_roles],
    )
