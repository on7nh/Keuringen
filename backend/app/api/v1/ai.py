from __future__ import annotations

import uuid
from datetime import date, datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_permission
from app.core.database import get_db
from app.models.ai import AIFeedback, AIFieldPrediction, AIJob
from app.models.documents import Document
from app.models.inspections import InspectionReport, InspectionStatus
from app.models.user import User
from app.schemas.ai import AIProposalCorrectRequest, AIProposalOut

router = APIRouter(tags=["ai"])


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _get_document_or_404(db: Session, document_id: uuid.UUID) -> Document:
    document = db.get(Document, document_id)
    if document is None or document.deleted_at is not None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Document not found")
    return document


def _get_prediction_for_document(db: Session, document: Document, prediction_id: uuid.UUID) -> AIFieldPrediction:
    prediction = db.get(AIFieldPrediction, prediction_id)
    if prediction is None or prediction.ai_job.document_version_id != document.current_version_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Proposal not found")
    return prediction


def _apply_prediction_value(db: Session, document: Document, field_code: str, value: str) -> None:
    """Pre-fills the relevant inspection field with a reviewed value. This
    never finalizes the inspection - POST /inspections/{id}/validate remains
    the only way to confirm a keuringsstatus and lock the record, per
    docs/01: "AI doet voorstellen, maar de gebruiker behoudt steeds de
    eindcontrole"."""
    inspection = db.query(InspectionReport).filter(InspectionReport.document_id == document.id).first()
    if inspection is None:
        raise HTTPException(status.HTTP_409_CONFLICT, detail="Geen keuringsrapport gekoppeld aan dit document")

    if field_code in ("EXAMINATION_DATE", "REPORT_DATE"):
        try:
            parsed_date = date.fromisoformat(value)
        except ValueError:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=f"Ongeldige datum '{value}', verwacht YYYY-MM-DD")
        if field_code == "EXAMINATION_DATE":
            inspection.inspection_date = parsed_date
            inspection.inspection_date_source = "AI_PROPOSAL"
        else:
            inspection.report_date = parsed_date
    elif field_code == "INSPECTION_STATUS":
        status_row = db.query(InspectionStatus).filter(InspectionStatus.code == value).first()
        if status_row is None:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=f"Onbekende keuringsstatus '{value}'")
        inspection.inspection_status_id = status_row.id
    else:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=f"Niet-ondersteund veld '{field_code}'")


@router.get("/documents/{document_id}/ai-proposals", response_model=list[AIProposalOut])
def list_ai_proposals(
    document_id: uuid.UUID, db: Session = Depends(get_db), _: User = Depends(get_current_user)
):
    document = _get_document_or_404(db, document_id)
    if document.current_version_id is None:
        return []

    latest_job = (
        db.query(AIJob)
        .filter(AIJob.document_version_id == document.current_version_id)
        .order_by(AIJob.queued_at.desc())
        .first()
    )
    if latest_job is None:
        return []

    return (
        db.query(AIFieldPrediction)
        .filter(AIFieldPrediction.ai_job_id == latest_job.id)
        .all()
    )


@router.post(
    "/documents/{document_id}/ai-proposals/{proposal_id}/confirm",
    response_model=AIProposalOut,
    dependencies=[Depends(require_permission("ai.feedback.manage"))],
)
def confirm_ai_proposal(
    document_id: uuid.UUID,
    proposal_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    document = _get_document_or_404(db, document_id)
    prediction = _get_prediction_for_document(db, document, proposal_id)

    value = prediction.proposed_value["value"]
    _apply_prediction_value(db, document, prediction.field_code, value)

    prediction.is_reviewed = True
    db.add(
        AIFeedback(
            ai_field_prediction_id=prediction.id,
            proposed_value=prediction.proposed_value,
            confirmed_value={"value": value},
            was_correct=True,
            corrected_at=_now(),
            corrected_by=user.id,
        )
    )
    db.commit()
    db.refresh(prediction)
    return prediction


@router.post(
    "/documents/{document_id}/ai-proposals/{proposal_id}/correct",
    response_model=AIProposalOut,
    dependencies=[Depends(require_permission("ai.feedback.manage"))],
)
def correct_ai_proposal(
    document_id: uuid.UUID,
    proposal_id: uuid.UUID,
    payload: AIProposalCorrectRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    document = _get_document_or_404(db, document_id)
    prediction = _get_prediction_for_document(db, document, proposal_id)

    _apply_prediction_value(db, document, prediction.field_code, payload.value)

    prediction.is_reviewed = True
    db.add(
        AIFeedback(
            ai_field_prediction_id=prediction.id,
            proposed_value=prediction.proposed_value,
            confirmed_value={"value": payload.value},
            was_correct=False,
            correction_reason=payload.reason,
            corrected_at=_now(),
            corrected_by=user.id,
        )
    )
    db.commit()
    db.refresh(prediction)
    return prediction
