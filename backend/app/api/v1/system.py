from __future__ import annotations

import shutil
import time
from pathlib import Path

import redis as redis_lib
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api.deps import require_permission
from app.core.config import get_settings
from app.core.database import get_db

router = APIRouter(tags=["system"])
settings = get_settings()


def _check_postgresql(db: Session) -> dict:
    start = time.monotonic()
    try:
        db.execute(text("SELECT 1"))
        return {
            "name": "postgresql",
            "label": "PostgreSQL",
            "status": "ok",
            "detail": None,
            "latency_ms": round((time.monotonic() - start) * 1000, 1),
        }
    except Exception as exc:
        return {"name": "postgresql", "label": "PostgreSQL", "status": "error", "detail": str(exc), "latency_ms": None}


def _check_redis() -> dict:
    start = time.monotonic()
    try:
        client = redis_lib.from_url(settings.redis_url, socket_connect_timeout=2)
        client.ping()
        return {
            "name": "redis",
            "label": "Redis",
            "status": "ok",
            "detail": None,
            "latency_ms": round((time.monotonic() - start) * 1000, 1),
        }
    except Exception as exc:
        return {"name": "redis", "label": "Redis", "status": "error", "detail": str(exc), "latency_ms": None}


def _check_document_storage() -> dict:
    """Verifies the document storage path is reachable and writable, per
    docs/20 section 22 (readiness must include write access to storage).
    This covers a locally mounted path as well as an NFS/SMB-mounted NAS
    share, since both simply appear as `DOCUMENT_STORAGE_PATH` to the app.
    """
    try:
        path = Path(settings.document_storage_path)
        path.mkdir(parents=True, exist_ok=True)
        probe = path / ".health-check"
        probe.write_text("ok")
        probe.unlink()
        total, _used, free = shutil.disk_usage(path)
        free_gib = free // (1024**3)
        total_gib = total // (1024**3)
        return {
            "name": "document_storage",
            "label": "Documentopslag (NAS/lokaal)",
            "status": "ok",
            "detail": f"{free_gib} GiB vrij van {total_gib} GiB",
            "latency_ms": None,
        }
    except Exception as exc:
        return {
            "name": "document_storage",
            "label": "Documentopslag (NAS/lokaal)",
            "status": "error",
            "detail": str(exc),
            "latency_ms": None,
        }


def _check_ai_gateway() -> dict:
    if not settings.ai_gateway_url:
        return {
            "name": "ai_gateway",
            "label": "AI Gateway",
            "status": "not_configured",
            "detail": "AI_GATEWAY_URL is niet ingesteld",
            "latency_ms": None,
        }
    return {
        "name": "ai_gateway",
        "label": "AI Gateway",
        "status": "unknown",
        "detail": "Nog niet geïmplementeerd (zie docs/04 en PROGRESS.md)",
        "latency_ms": None,
    }


@router.get("/system/status", dependencies=[Depends(require_permission("settings.manage"))])
def system_status(db: Session = Depends(get_db)):
    checks = [
        _check_postgresql(db),
        _check_redis(),
        _check_document_storage(),
        _check_ai_gateway(),
    ]
    overall = "degraded" if any(c["status"] == "error" for c in checks) else "ok"
    return {"status": overall, "checks": checks}
