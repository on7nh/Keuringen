"""Seeds reference data that the application cannot function without:
permissions, roles, inspection statuses and a first system administrator.

Run once after migrating: `python -m app.seed`
"""

from __future__ import annotations

import os

from app.core.database import SessionLocal
from app.core.security import hash_password
from app.models.inspections import InspectionStatus
from app.models.rbac import Permission, Role, RolePermission
from app.models.user import User
from app.services.auth_service import confirm_totp, setup_totp

PERMISSIONS = [
    "organizations.manage",
    "sites.manage",
    "documents.read",
    "documents.upload",
    "documents.validate",
    "inspections.manage",
    "risk_analyses.manage",
    "ai.feedback.manage",
    "knowledge.approve",
    "settings.manage",
    "audit.read",
    "authentication.policy.manage",
    "authentication.credentials.manage",
    "sessions.manage",
]

# code, name, scope
ROLES = [
    ("SYSTEM_ADMIN", "Administrator", "system"),
    ("USER", "Gebruiker", "organization"),
    ("SITE_FACILITY_MANAGER", "Site Facility Manager", "site"),
    ("SITE_MANAGER", "Site Manager", "site"),
]

INSPECTION_STATUSES = [
    ("UNCONFIRMED", "-------------", 0),
    ("APPROVED", "Goedgekeurd", 1),
    ("APPROVED_WITH_REMARKS", "Goedgekeurd met opmerkingen", 2),
    ("REJECTED", "Afgekeurd", 3),
]


def seed() -> None:
    db = SessionLocal()
    try:
        permission_by_code = {}
        for code in PERMISSIONS:
            perm = db.query(Permission).filter(Permission.code == code).first()
            if perm is None:
                perm = Permission(code=code)
                db.add(perm)
                db.flush()
            permission_by_code[code] = perm

        for code, name, scope in ROLES:
            role = db.query(Role).filter(Role.code == code).first()
            if role is None:
                role = Role(code=code, name=name, scope=scope, is_system_role=True)
                db.add(role)
                db.flush()
            if code == "SYSTEM_ADMIN":
                existing_permission_ids = {rp.permission_id for rp in role.permissions}
                for perm in permission_by_code.values():
                    if perm.id not in existing_permission_ids:
                        db.add(RolePermission(role_id=role.id, permission_id=perm.id))

        for code, label, order in INSPECTION_STATUSES:
            status_row = db.query(InspectionStatus).filter(InspectionStatus.code == code).first()
            if status_row is None:
                db.add(InspectionStatus(code=code, label=label, display_order=order))

        db.commit()

        admin_email = os.environ.get("SEED_ADMIN_EMAIL")
        admin_password = os.environ.get("SEED_ADMIN_PASSWORD")
        if admin_email and admin_password:
            existing = db.query(User).filter(User.email == admin_email).first()
            if existing is None:
                admin = User(
                    email=admin_email,
                    display_name="System Administrator",
                    password_hash=hash_password(admin_password),
                    is_system_admin=True,
                    strong_authentication_required=True,
                )
                db.add(admin)
                db.commit()
                db.refresh(admin)

                # Bootstrap a first strong authentication method so the new
                # admin is not locked out by the "strong auth required"
                # policy on the very first login (see docs/01 section on
                # strong authentication). This runs through the same
                # setup/confirm flow a user would use, not a bypass.
                import pyotp

                registration_id, secret, otpauth_uri = setup_totp(db, admin)
                confirmation_code = pyotp.TOTP(secret).now()
                confirm_totp(db, admin, registration_id, confirmation_code)

                print(f"Created system admin user: {admin_email}")
                print(f"Bootstrap TOTP secret (add to an authenticator app now): {secret}")
                print(f"otpauth URI: {otpauth_uri}")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
    print("Seed data applied.")
