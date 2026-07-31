from __future__ import annotations

import shutil
import subprocess
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


def _git(*args: str) -> str:
    result = subprocess.run(
        ["git", "-C", settings.repo_path, "-c", "safe.directory=*", *args],
        capture_output=True,
        text=True,
        timeout=10,
        check=True,
    )
    return result.stdout.strip()


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

    The NAS connection itself is a host-level concern (NFS/SMB mount into
    `DOCUMENT_STORAGE_PATH`, per docs/20 section 12) - there is no
    in-app credential to configure. This check exists to make a broken or
    missing host mount immediately visible, with the exact path and error
    so it can be diagnosed on the host.
    """
    path = Path(settings.document_storage_path)
    try:
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
            "detail": f"{path}: {free_gib} GiB vrij van {total_gib} GiB",
            "latency_ms": None,
        }
    except Exception as exc:
        return {
            "name": "document_storage",
            "label": "Documentopslag (NAS/lokaal)",
            "status": "error",
            "detail": f"{path}: {exc} — controleer de NAS-mount op de host (docs/20 §12)",
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


def _check_update_available() -> dict:
    """Read-only comparison of the running commit against the latest commit
    on the deployed branch upstream. Deliberately does not fetch, pull, or
    restart anything - the app container has no way to change itself. An
    admin decides whether and when to actually pull and rebuild.
    """
    label = "Software-update"
    try:
        local_sha = _git("rev-parse", "HEAD")
        remote_output = _git("ls-remote", "origin", f"refs/heads/{settings.repo_branch}")
        if not remote_output:
            return {
                "name": "update_available",
                "label": label,
                "status": "unknown",
                "detail": f"Branch '{settings.repo_branch}' niet gevonden op origin",
                "latency_ms": None,
            }
        remote_sha = remote_output.split()[0]
    except Exception as exc:
        return {
            "name": "update_available",
            "label": label,
            "status": "unknown",
            "detail": f"Kon geen update-check uitvoeren: {exc}",
            "latency_ms": None,
        }

    if local_sha == remote_sha:
        return {
            "name": "update_available",
            "label": label,
            "status": "ok",
            "detail": f"Actueel op {settings.repo_branch} ({local_sha[:7]})",
            "latency_ms": None,
        }

    return {
        "name": "update_available",
        "label": label,
        "status": "update_available",
        "detail": (
            f"Nieuwe versie op {settings.repo_branch}: {local_sha[:7]} -> {remote_sha[:7]}. "
            "Draai op de VM: git pull && docker compose build --pull && docker compose up -d"
        ),
        "latency_ms": None,
    }


@router.get("/system/status", dependencies=[Depends(require_permission("settings.manage"))])
def system_status(db: Session = Depends(get_db)):
    checks = [
        _check_postgresql(db),
        _check_redis(),
        _check_document_storage(),
        _check_ai_gateway(),
        _check_update_available(),
    ]
    overall = "degraded" if any(c["status"] == "error" for c in checks) else "ok"
    return {"status": overall, "checks": checks}
