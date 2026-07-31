"""Central naming service — the single source of truth for file names and
physical storage paths, per docs/02_Technisch_Ontwerp.md section 6.3.

No other module may assemble a definitive file name or storage path. All
callers must go through `NamingService` so the naming convention, sequence
numbering and physical-folder immutability rules stay enforced in one place.

Convention:
    Site_Sitenummer_Disciplinecode_Documenttypecode_DatumTijd.ext
Example:
    Aalst_36_HOO_FOT_20260606133325.jpg

File name generation is always sequential per site (docs/02 section 6.3.2):
callers must hold `NamingService.site_lock` for the site while reserving a
name, to avoid duplicate sequence numbers or partially overwritten files.
"""

from __future__ import annotations

import re
import unicodedata
import uuid
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.documents import Document, DocumentVersion
from app.models.organization import Site

settings = get_settings()

_INVALID_CHARS_RE = re.compile(r"[^A-Za-z0-9]+")
MAX_FILENAME_LENGTH = 180


def _normalize_component(value: str) -> str:
    """Strip accents/spaces and keep only alphanumerics, per the naming
    convention's requirement to normalize allowed characters and separators.
    """
    normalized = unicodedata.normalize("NFKD", value)
    ascii_only = normalized.encode("ascii", "ignore").decode("ascii")
    cleaned = _INVALID_CHARS_RE.sub("", ascii_only)
    return cleaned


def generate_storage_code(sequence: int) -> str:
    return f"SITE_{sequence:08d}"


def build_site_identifier(site: Site) -> str:
    """Visible Site identification used in filenames and the UI, e.g.
    'Aalst_36' or, for a site awaiting a definitive number, 'Putte_TMP001'."""
    name_part = _normalize_component(site.name)
    number_part = _normalize_component(site.site_number)
    return f"{name_part}_{number_part}"


@contextmanager
def site_lock(db: Session, site_id: uuid.UUID):
    """Postgres advisory lock, scoped to the site, serializing all file-name
    generation and mutation for that site (docs/02 section 6.3.2)."""
    lock_key = int(uuid.UUID(str(site_id)).int % (2**63))
    db.execute(text("SELECT pg_advisory_xact_lock(:key)"), {"key": lock_key})
    yield


class NamingService:
    """Generates and validates file names according to the central
    convention. Must be called one file at a time, holding `site_lock`.
    """

    def __init__(self, db: Session):
        self.db = db

    def storage_root(self, site: Site) -> Path:
        return Path(settings.document_storage_path) / site.storage_relative_path

    def build_document_directory(
        self, site: Site, document_id: uuid.UUID, version_id: uuid.UUID
    ) -> Path:
        return self.storage_root(site) / str(document_id) / str(version_id)

    def propose_filename(
        self,
        *,
        site: Site,
        discipline_code: str,
        document_type_code: str,
        timestamp: datetime,
        extension: str,
    ) -> str:
        site_identifier = build_site_identifier(site)
        discipline = _normalize_component(discipline_code)
        doc_type = _normalize_component(document_type_code)
        datetime_part = timestamp.strftime("%Y%m%d%H%M%S")
        ext = extension.lower().lstrip(".")

        base_name = f"{site_identifier}_{discipline}_{doc_type}_{datetime_part}"
        candidate = f"{base_name}.{ext}"

        if len(candidate) > MAX_FILENAME_LENGTH:
            raise ValueError("Generated filename exceeds the maximum allowed length")

        return self._resolve_conflict(site, base_name, ext)

    def _resolve_conflict(self, site: Site, base_name: str, ext: str) -> str:
        """Appends a sequence number as the last component before the
        extension when a name conflict is found (docs/02 section 6.3.3).
        Must be called while holding `site_lock` for this site.
        """
        candidate = f"{base_name}.{ext}"
        existing = (
            self.db.query(DocumentVersion)
            .join(Document, Document.id == DocumentVersion.document_id)
            .filter(Document.site_id == site.id, DocumentVersion.stored_filename == candidate)
            .first()
        )
        if existing is None:
            return candidate

        sequence = 1
        while True:
            candidate = f"{base_name}_{sequence:02d}.{ext}"
            existing = (
                self.db.query(DocumentVersion)
                .join(Document, Document.id == DocumentVersion.document_id)
                .filter(Document.site_id == site.id, DocumentVersion.stored_filename == candidate)
                .first()
            )
            if existing is None:
                return candidate
            sequence += 1

    def validate_extension(self, filename: str) -> str:
        ext = Path(filename).suffix.lower()
        if ext not in settings.allowed_upload_extensions:
            raise ValueError(f"File extension '{ext}' is not permitted")
        return ext
