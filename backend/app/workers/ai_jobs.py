"""AI job worker: document field extraction, per docs/02 section 5 (AI Job
Flow) and docs/01 ("Herkende gegevens"). Runs OCR/text extraction and rule-
based (or optional LLM-gateway) field extraction, then stores the result as
review-pending proposals - never as a definitive value. See
app/api/v1/ai.py for the confirm/correct endpoints that apply them.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from pathlib import Path

from app.celery_app import celery_app
from app.core.config import get_settings
from app.core.database import SessionLocal
from app.models.ai import (
    JOB_STATUS_COMPLETED,
    JOB_STATUS_FAILED,
    JOB_STATUS_RUNNING,
    AIFieldPrediction,
    AIJob,
)
from app.models.documents import Document, DocumentVersion
from app.services.ai.field_extraction import extract_fields
from app.services.ai.text_extraction import extract_text

logger = logging.getLogger(__name__)
settings = get_settings()


def _now() -> datetime:
    return datetime.now(timezone.utc)


@celery_app.task(name="app.workers.ai_jobs.run_document_field_extraction")
def run_document_field_extraction(document_version_id: str) -> str:
    db = SessionLocal()
    try:
        version = db.get(DocumentVersion, document_version_id)
        if version is None:
            logger.warning("AI job skipped: document_version %s not found", document_version_id)
            return "SKIPPED"
        document = db.get(Document, version.document_id)

        job = AIJob(
            document_version_id=version.id,
            job_type="DOCUMENT_FIELD_EXTRACTION",
            status=JOB_STATUS_RUNNING,
            queued_at=_now(),
            started_at=_now(),
        )
        db.add(job)
        document.ai_status = "PROCESSING"
        db.commit()
        db.refresh(job)

        start = _now()
        try:
            file_path = Path(settings.document_storage_path) / version.storage_path
            text = extract_text(file_path, version.file_extension)
            predictions, model_identifier = extract_fields(text)

            for field_code, data in predictions.items():
                db.add(
                    AIFieldPrediction(
                        ai_job_id=job.id,
                        field_code=field_code,
                        proposed_value={"value": data["value"]},
                        confidence=data.get("confidence"),
                        source_snippet=data.get("snippet"),
                    )
                )

            job.model_identifier = model_identifier
            job.validated_response = predictions
            job.status = JOB_STATUS_COMPLETED
            job.finished_at = _now()
            job.duration_ms = int((job.finished_at - start).total_seconds() * 1000)
            document.ai_status = "COMPLETED" if predictions else "NO_PROPOSALS"
            db.commit()
            return JOB_STATUS_COMPLETED
        except Exception as exc:
            db.rollback()
            job = db.get(AIJob, job.id)
            document = db.get(Document, version.document_id)
            job.status = JOB_STATUS_FAILED
            job.finished_at = _now()
            job.error_message = str(exc)[:1024]
            document.ai_status = "FAILED"
            db.commit()
            logger.exception("AI job failed for document_version %s", document_version_id)
            return JOB_STATUS_FAILED
    finally:
        db.close()
