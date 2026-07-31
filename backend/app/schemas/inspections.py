from __future__ import annotations

import uuid
from datetime import date, datetime

from pydantic import BaseModel


class InspectionStatusOut(BaseModel):
    id: uuid.UUID
    code: str
    label: str
    display_order: int

    model_config = {"from_attributes": True}


class InspectionFindingOut(BaseModel):
    id: uuid.UUID
    finding_number: str | None
    severity: str
    description: str
    arei_reference: str | None
    is_resolved: bool

    model_config = {"from_attributes": True}


class InspectionFindingCreate(BaseModel):
    finding_number: str | None = None
    severity: str
    description: str
    arei_reference: str | None = None


class InspectionReportOut(BaseModel):
    id: uuid.UUID
    document_id: uuid.UUID
    inspection_date: date | None
    inspection_date_source: str | None
    report_date: date | None
    expiry_date: date | None
    inspection_status_id: uuid.UUID
    certificate_number: str | None
    remarks: str | None
    validated_at: datetime | None

    model_config = {"from_attributes": True}


class InspectionReportUpdate(BaseModel):
    inspection_date: date | None = None
    report_date: date | None = None
    expiry_date: date | None = None
    inspection_status_id: uuid.UUID | None = None
    certificate_number: str | None = None
    remarks: str | None = None


class InspectionValidateRequest(BaseModel):
    inspection_status_id: uuid.UUID
    inspection_date: date
    expiry_date: date | None = None


class InspectionScheduleOut(BaseModel):
    id: uuid.UUID
    site_id: uuid.UUID
    installation_id: uuid.UUID | None
    discipline_id: uuid.UUID
    next_due_date: date
    status: str

    model_config = {"from_attributes": True}
