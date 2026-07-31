from __future__ import annotations

import uuid
from datetime import date, datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_permission
from app.core.database import get_db
from app.models.documents import Document
from app.models.inspections import (
    UNCONFIRMED_STATUS_CODE,
    InspectionFinding,
    InspectionReport,
    InspectionSchedule,
    InspectionStatus,
)
from app.models.organization import Discipline
from app.models.user import User
from app.schemas.inspections import (
    InspectionFindingCreate,
    InspectionFindingOut,
    InspectionReportOut,
    InspectionReportUpdate,
    InspectionScheduleOut,
    InspectionStatusOut,
    InspectionValidateRequest,
)
from app.services.inspection_service import calculate_expiry_date

router = APIRouter(tags=["inspections"])


@router.get("/inspection-statuses", response_model=list[InspectionStatusOut])
def list_inspection_statuses(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return db.query(InspectionStatus).order_by(InspectionStatus.display_order).all()


@router.get("/inspections", response_model=list[InspectionReportOut])
def list_inspections(
    site_id: uuid.UUID | None = None,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    query = db.query(InspectionReport)
    if site_id:
        query = query.join(Document, Document.id == InspectionReport.document_id).filter(
            Document.site_id == site_id
        )
    return query.all()


@router.get("/inspections/due", response_model=list[InspectionScheduleOut])
def inspections_due(
    within_days: int = 90,
    site_id: uuid.UUID | None = None,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    cutoff = date.today() + timedelta(days=within_days)
    query = db.query(InspectionSchedule).filter(
        InspectionSchedule.status == "OPEN", InspectionSchedule.next_due_date <= cutoff
    )
    if site_id:
        query = query.filter(InspectionSchedule.site_id == site_id)
    return query.order_by(InspectionSchedule.next_due_date).all()


@router.get("/inspections/{inspection_id}", response_model=InspectionReportOut)
def get_inspection(inspection_id: uuid.UUID, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    inspection = db.get(InspectionReport, inspection_id)
    if inspection is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Inspection not found")
    return inspection


@router.patch(
    "/inspections/{inspection_id}",
    response_model=InspectionReportOut,
    dependencies=[Depends(require_permission("inspections.manage"))],
)
def update_inspection(
    inspection_id: uuid.UUID,
    payload: InspectionReportUpdate,
    db: Session = Depends(get_db),
):
    inspection = db.get(InspectionReport, inspection_id)
    if inspection is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Inspection not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(inspection, field, value)
    db.commit()
    db.refresh(inspection)
    return inspection


@router.post(
    "/inspections/{inspection_id}/validate",
    response_model=InspectionReportOut,
    dependencies=[Depends(require_permission("inspections.manage"))],
)
def validate_inspection(
    inspection_id: uuid.UUID,
    payload: InspectionValidateRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Confirms the manually-checked inspection status and date, per
    docs/01_Functioneel_Ontwerp.md validation rules: a report cannot be
    finalized while the status is still the UNCONFIRMED placeholder."""
    inspection = db.get(InspectionReport, inspection_id)
    if inspection is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Inspection not found")

    status_row = db.get(InspectionStatus, payload.inspection_status_id)
    if status_row is None or status_row.code == UNCONFIRMED_STATUS_CODE:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, detail="DOCUMENT_VALIDATION_FAILED")

    document = db.get(Document, inspection.document_id)
    discipline = db.get(Discipline, document.discipline_id)

    expiry_date = payload.expiry_date or calculate_expiry_date(
        discipline, inspection_date=payload.inspection_date, report_date=inspection.report_date
    )
    if discipline.validity_value is not None and expiry_date is None:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, detail="DOCUMENT_VALIDATION_FAILED")

    inspection.inspection_status_id = status_row.id
    inspection.inspection_date = payload.inspection_date
    inspection.expiry_date = expiry_date
    inspection.validated_at = datetime.now(timezone.utc)
    inspection.validated_by = user.id

    document.validation_status = "VALIDATED"
    document.validated_at = inspection.validated_at
    document.validated_by = user.id
    document.row_version += 1

    if expiry_date is not None:
        schedule = (
            db.query(InspectionSchedule)
            .filter(
                InspectionSchedule.site_id == document.site_id,
                InspectionSchedule.installation_id == document.installation_id,
                InspectionSchedule.discipline_id == document.discipline_id,
                InspectionSchedule.status == "OPEN",
            )
            .first()
        )
        if schedule is None:
            schedule = InspectionSchedule(
                site_id=document.site_id,
                installation_id=document.installation_id,
                discipline_id=document.discipline_id,
                next_due_date=expiry_date,
                source_report_id=inspection.id,
                status="OPEN",
            )
            db.add(schedule)
        else:
            schedule.next_due_date = expiry_date
            schedule.source_report_id = inspection.id

    db.commit()
    db.refresh(inspection)
    return inspection


@router.post(
    "/inspections/{inspection_id}/findings",
    response_model=InspectionFindingOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("inspections.manage"))],
)
def add_finding(inspection_id: uuid.UUID, payload: InspectionFindingCreate, db: Session = Depends(get_db)):
    inspection = db.get(InspectionReport, inspection_id)
    if inspection is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Inspection not found")
    finding = InspectionFinding(inspection_report_id=inspection_id, **payload.model_dump())
    db.add(finding)
    db.commit()
    db.refresh(finding)
    return finding


@router.patch(
    "/inspections/{inspection_id}/findings/{finding_id}",
    response_model=InspectionFindingOut,
    dependencies=[Depends(require_permission("inspections.manage"))],
)
def update_finding(
    inspection_id: uuid.UUID,
    finding_id: uuid.UUID,
    payload: InspectionFindingCreate,
    db: Session = Depends(get_db),
):
    finding = db.get(InspectionFinding, finding_id)
    if finding is None or finding.inspection_report_id != inspection_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Finding not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(finding, field, value)
    db.commit()
    db.refresh(finding)
    return finding
