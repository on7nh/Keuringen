from __future__ import annotations

import hashlib
import shutil
import uuid
from datetime import datetime, timezone
from pathlib import Path

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.documents import Document, DocumentType, DocumentVersion
from app.models.inspections import UNCONFIRMED_STATUS_CODE, InspectionReport, InspectionStatus
from app.models.organization import Discipline, Site
from app.services.naming_service import NamingService, site_lock

settings = get_settings()


def _now() -> datetime:
    return datetime.now(timezone.utc)


MIME_TYPES_BY_EXTENSION = {
    ".pdf": "application/pdf",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".dwg": "application/acad",
    ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
}


def _write_to_quarantine(upload: UploadFile, extension: str) -> tuple[Path, str, int]:
    quarantine_dir = Path(settings.document_storage_path) / "_quarantine"
    quarantine_dir.mkdir(parents=True, exist_ok=True)
    temp_path = quarantine_dir / f"{uuid.uuid4()}{extension}"

    sha256 = hashlib.sha256()
    size = 0
    with temp_path.open("wb") as out_file:
        while chunk := upload.file.read(1024 * 1024):
            size += len(chunk)
            if size > settings.max_upload_size_bytes:
                temp_path.unlink(missing_ok=True)
                raise HTTPException(status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="File exceeds 100 MB")
            sha256.update(chunk)
            out_file.write(chunk)

    if size == 0:
        temp_path.unlink(missing_ok=True)
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Empty file")

    return temp_path, sha256.hexdigest(), size


def upload_document(
    db: Session,
    *,
    site_id: uuid.UUID,
    discipline_id: uuid.UUID,
    document_type_id: uuid.UUID,
    installation_id: uuid.UUID | None,
    upload: UploadFile,
    uploaded_by: uuid.UUID,
    document_id: uuid.UUID | None = None,
) -> Document:
    """Validates, stores and registers an uploaded file as a new Document
    (or a new version of an existing one), per docs/02 sections 6.1-6.3.

    File-name generation and the final move into site storage happen while
    holding the site's advisory lock, so mutations stay strictly one file at
    a time within that site (docs/02 section 6.3.2).
    """
    site = db.get(Site, site_id)
    if site is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Site not found")
    discipline = db.get(Discipline, discipline_id)
    if discipline is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Discipline not found")
    document_type = db.get(DocumentType, document_type_id)
    if document_type is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Document type not found")

    naming = NamingService(db)
    extension = naming.validate_extension(upload.filename or "")

    temp_path, file_hash, file_size = _write_to_quarantine(upload, extension)

    try:
        with site_lock(db, site.id):
            duplicate = (
                db.query(DocumentVersion)
                .join(Document, Document.id == DocumentVersion.document_id)
                .filter(Document.site_id == site.id, DocumentVersion.file_hash_sha256 == file_hash)
                .first()
            )
            if duplicate is not None:
                raise HTTPException(status.HTTP_409_CONFLICT, detail="DUPLICATE_FILE")

            if document_id is not None:
                document = db.get(Document, document_id)
                if document is None or document.site_id != site.id:
                    raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Document not found")
                version_number = len(document.versions) + 1
            else:
                document = Document(
                    organization_id=site.organization_id,
                    site_id=site.id,
                    installation_id=installation_id,
                    discipline_id=discipline_id,
                    document_type_id=document_type_id,
                    created_by=uploaded_by,
                )
                db.add(document)
                db.flush()
                version_number = 1

                if document_type.requires_inspection_data:
                    # The report always starts with the mandatory UNCONFIRMED
                    # placeholder status, per docs/01: "Elke keuring moet
                    # manueel gecontroleerd en bevestigd worden." AI field
                    # extraction below only produces proposals for review -
                    # it never sets this directly.
                    unconfirmed = (
                        db.query(InspectionStatus)
                        .filter(InspectionStatus.code == UNCONFIRMED_STATUS_CODE)
                        .first()
                    )
                    if unconfirmed is not None:
                        db.add(InspectionReport(document_id=document.id, inspection_status_id=unconfirmed.id))

            timestamp = _now()
            filename = naming.propose_filename(
                site=site,
                discipline_code=discipline.code,
                document_type_code=document_type.code,
                timestamp=timestamp,
                extension=extension,
            )

            version_id = uuid.uuid4()
            destination_dir = naming.build_document_directory(site, document.id, version_id)
            destination_dir.mkdir(parents=True, exist_ok=True)
            destination_path = destination_dir / filename
            shutil.move(str(temp_path), str(destination_path))

            version = DocumentVersion(
                id=version_id,
                document_id=document.id,
                version_number=version_number,
                storage_path=str(destination_path.relative_to(settings.document_storage_path)),
                stored_filename=filename,
                original_filename=upload.filename or filename,
                file_hash_sha256=file_hash,
                file_size_bytes=file_size,
                mime_type=MIME_TYPES_BY_EXTENSION.get(extension, "application/octet-stream"),
                file_extension=extension,
                uploaded_at=timestamp,
                uploaded_by=uploaded_by,
                is_quarantined=False,
                malware_scan_status="SKIPPED",
            )
            db.add(version)
            db.flush()
            document.current_version_id = version.id
            db.commit()
            db.refresh(document)

            if document_type.supports_ai_analysis and extension in (".pdf", ".jpg", ".jpeg"):
                from app.workers.ai_jobs import run_document_field_extraction

                run_document_field_extraction.delay(str(version.id))

            return document
    finally:
        temp_path.unlink(missing_ok=True)
