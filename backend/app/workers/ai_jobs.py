"""AI job worker tasks, per docs/02 section 5 (AI job flow).

This is a scaffold: it registers the job lifecycle (queued -> validated
result) but does not yet call a real OCR/vision/LLM backend. Wiring an
actual model server is future work (see docs/04_AI_Knowledge_Platform_Ontwerp.md).
"""

from __future__ import annotations

from app.celery_app import celery_app


@celery_app.task(name="app.workers.ai_jobs.run_document_analysis")
def run_document_analysis(document_version_id: str, job_type: str) -> dict:
    raise NotImplementedError(
        "AI model integration is not yet implemented; see docs/04 for the planned design."
    )
