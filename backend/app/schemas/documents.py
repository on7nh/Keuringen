from __future__ import annotations

import uuid
from datetime import date, datetime

from pydantic import BaseModel


class DocumentVersionOut(BaseModel):
    id: uuid.UUID
    version_number: int
    stored_filename: str
    original_filename: str
    file_size_bytes: int
    mime_type: str
    uploaded_at: datetime
    is_quarantined: bool

    model_config = {"from_attributes": True}


class DocumentOut(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    site_id: uuid.UUID
    installation_id: uuid.UUID | None
    discipline_id: uuid.UUID
    document_type_id: uuid.UUID
    title: str | None
    document_date: date | None
    document_date_source: str | None
    ai_status: str
    validation_status: str
    sharepoint_marked: bool
    row_version: int

    model_config = {"from_attributes": True}


class DocumentUpdate(BaseModel):
    title: str | None = None
    document_date: date | None = None
    discipline_id: uuid.UUID | None = None
    installation_id: uuid.UUID | None = None
    row_version: int


class DocumentValidateRequest(BaseModel):
    row_version: int


class UploadInitRequest(BaseModel):
    site_id: uuid.UUID
    discipline_id: uuid.UUID
    document_type_id: uuid.UUID
    installation_id: uuid.UUID | None = None
    original_filename: str
    document_id: uuid.UUID | None = None  # set when adding a new version to an existing document


class UploadInitResponse(BaseModel):
    upload_id: uuid.UUID
    document_id: uuid.UUID
    version_number: int
