from __future__ import annotations

import uuid

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_token, is_step_up_valid
from app.models.auth import UserSession
from app.models.rbac import Permission, Role, RolePermission, UserOrganizationRole, UserSiteRole
from app.models.user import User

bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    if credentials is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    try:
        payload = decode_token(credentials.credentials)
    except ValueError as exc:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from exc

    if payload.get("type") != "access":
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")

    user = db.get(User, uuid.UUID(payload["sub"]))
    if user is None or not user.is_active or user.deleted_at is not None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Account is not active")

    session_id = payload.get("session_id")
    if session_id:
        session = db.get(UserSession, uuid.UUID(session_id))
        if session is None or session.revoked_at is not None:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Session has been revoked")

    return user


def get_current_session(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> UserSession | None:
    if credentials is None:
        return None
    try:
        payload = decode_token(credentials.credentials)
    except ValueError:
        return None
    session_id = payload.get("session_id")
    if not session_id:
        return None
    return db.get(UserSession, uuid.UUID(session_id))


def require_step_up(action: str):
    def _dependency(
        session: UserSession | None = Depends(get_current_session),
    ) -> None:
        if session is None or not is_step_up_valid(session.step_up_authenticated_at):
            raise HTTPException(
                status.HTTP_403_FORBIDDEN,
                detail={
                    "error": {
                        "code": "STEP_UP_REQUIRED",
                        "message": "Voor deze actie is aanvullende verificatie vereist.",
                        "details": {"intended_action": action},
                    }
                },
            )

    return _dependency


def _user_permission_codes(db: Session, user: User) -> set[str]:
    if user.is_system_admin:
        return {"*"}

    role_ids = {r.role_id for r in user.organization_roles} | {r.role_id for r in user.site_roles}
    if not role_ids:
        return set()

    codes = (
        db.query(Permission.code)
        .join(RolePermission, RolePermission.permission_id == Permission.id)
        .filter(RolePermission.role_id.in_(role_ids))
        .all()
    )
    return {c[0] for c in codes}


def require_permission(code: str):
    def _dependency(
        user: User = Depends(get_current_user), db: Session = Depends(get_db)
    ) -> User:
        codes = _user_permission_codes(db, user)
        if "*" in codes or code in codes:
            return user
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")

    return _dependency
