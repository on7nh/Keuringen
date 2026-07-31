from __future__ import annotations

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.organization import Site
from app.services.naming_service import generate_storage_code


def allocate_storage_code(db: Session) -> str:
    """Assigns the next unique, immutable physical storage code for a new
    Site, per docs/02 section 6.3.5. Once assigned, this value never
    changes even when the site name or number are corrected later."""
    max_sequence = db.query(func.count(Site.id)).scalar() or 0
    sequence = max_sequence + 1
    while True:
        candidate = generate_storage_code(sequence)
        exists = db.query(Site).filter(Site.storage_code == candidate).first()
        if exists is None:
            return candidate
        sequence += 1


def next_temporary_site_number(db: Session, organization_id) -> str:
    """Generates a unique TMPnnn code within the organization for a Site
    still awaiting its definitive site number, per docs/02 section 6.3.4."""
    existing = (
        db.query(Site.site_number)
        .filter(Site.organization_id == organization_id, Site.is_temporary_site_number.is_(True))
        .all()
    )
    used_numbers = set()
    for (site_number,) in existing:
        if site_number.startswith("TMP"):
            try:
                used_numbers.add(int(site_number[3:]))
            except ValueError:
                continue
    next_number = 1
    while next_number in used_numbers:
        next_number += 1
    return f"TMP{next_number:03d}"
