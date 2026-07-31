from __future__ import annotations

import uuid
from datetime import date, datetime, timezone

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_permission
from app.core.database import get_db
from app.models.documents import Document, DocumentVersion
from app.models.user import User
from app.schemas.documents import (
    DocumentOut,
    DocumentUpdate,
    DocumentValidateRequest,
    DocumentVersionOut,
)
from app.services.document_service import upload_document

router = APIRouter(tags=["documents"])


@router.get("/documents", response_model=list[DocumentOut])
def list_documents(
    site_id: uuid.UUID | None = None,
    discipline_id: uuid.UUID | None = None,
    validation_status: str | None = None,
    document_date_from: date | None = None,
    document_date_to: date | None = None,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    query = db.query(Document).filter(Document.deleted_at.is_(None))
    if site_id:
        query = query.filter(Document.site_id == site_id)
    if discipline_id:
        query = query.filter(Document.discipline_id == discipline_id)
    if validation_status:
        query = query.filter(Document.validation_status == validation_status)
    if document_date_from:
        query = query.filter(Document.document_date >= document_date_from)
    if document_date_to:
        query = query.filter(Document.document_date <= document_date_to)
    return query.order_by(Document.created_at.desc()).all()


@router.post(
    "/documents/upload",
    response_model=DocumentOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("documents.upload"))],
)
def upload(
    site_id: uuid.UUID = Form(...),
    discipline_id: uuid.UUID = Form(...),
    document_type_id: uuid.UUID = Form(...),
    installation_id: uuid.UUID | None = Form(None),
    document_id: uuid.UUID | None = Form(None),
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return upload_document(
        db,
        site_id=site_id,
        discipline_id=discipline_id,
        document_type_id=document_type_id,
        installation_id=installation_id,
        upload=file,
        uploaded_by=user.id,
        document_id=document_id,
    )


@router.get("/documents/{document_id}", response_model=DocumentOut)
def get_document(document_id: uuid.UUID, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    document = db.get(Document, document_id)
    if document is None or document.deleted_at is not None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Document not found")
    return document


@router.get("/documents/{document_id}/versions", response_model=list[DocumentVersionOut])
def list_document_versions(document_id: uuid.UUID, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    document = db.get(Document, document_id)
    if document is None or document.deleted_at is not None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Document not found")
    return (
        db.query(DocumentVersion)
        .filter(DocumentVersion.document_id == document_id)
        .order_by(DocumentVersion.version_number)
        .all()
    )


@router.patch(
    "/documents/{document_id}",
    response_model=DocumentOut,
    dependencies=[Depends(require_permission("documents.upload"))],
)
def update_document(
    document_id: uuid.UUID,
    payload: DocumentUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    document = db.get(Document, document_id)
    if document is None or document.deleted_at is not None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Document not found")
    if document.row_version != payload.row_version:
        raise HTTPException(status.HTTP_409_CONFLICT, detail="ROW_VERSION_CONFLICT")

    data = payload.model_dump(exclude={"row_version"}, exclude_unset=True)
    for field, value in data.items():
        setattr(document, field, value)
    document.row_version += 1
    document.updated_by = user.id
    db.commit()
    db.refresh(document)
    return document


@router.post(
    "/documents/{document_id}/validate",
    response_model=DocumentOut,
    dependencies=[Depends(require_permission("documents.validate"))],
)
def validate_document(
    document_id: uuid.UUID,
    payload: DocumentValidateRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    document = db.get(Document, document_id)
    if document is None or document.deleted_at is not None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Document not found")
    if document.row_version != payload.row_version:
        raise HTTPException(status.HTTP_409_CONFLICT, detail="ROW_VERSION_CONFLICT")

    if document.site_id is None or document.discipline_id is None:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, detail="DOCUMENT_VALIDATION_FAILED")

    document.validation_status = "VALIDATED"
    document.validated_at = datetime.now(timezone.utc)
    document.validated_by = user.id
    document.row_version += 1
    db.commit()
    db.refresh(document)
    return document
