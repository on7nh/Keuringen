from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.database import engine

settings = get_settings()

app = FastAPI(title="Digitaal Keurings- en Documentbeheer", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.public_base_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API routes are registered before the React static assets and catch-all
# fallback below, per docs/20 section 15 — /api, /health and /events must
# never fall through to index.html.
app.include_router(api_router, prefix="/api/v1")


@app.get("/health", include_in_schema=False)
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/v1/health", include_in_schema=False)
def api_health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/v1/health/ready", include_in_schema=False)
def api_health_ready() -> dict[str, str]:
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Database not reachable") from exc
    return {"status": "ready"}


DIST_DIR = Path(__file__).resolve().parent.parent / "frontend-dist"
ASSETS_DIR = DIST_DIR / "assets"

if ASSETS_DIR.exists():
    app.mount("/assets", StaticFiles(directory=ASSETS_DIR), name="assets")


@app.get("/{full_path:path}", include_in_schema=False)
def react_fallback(full_path: str):
    requested = (DIST_DIR / full_path).resolve()

    if DIST_DIR.resolve() not in requested.parents and requested != DIST_DIR.resolve():
        raise HTTPException(status_code=404)

    if full_path and requested.is_file():
        return FileResponse(requested)

    index_file = DIST_DIR / "index.html"
    if not index_file.is_file():
        raise HTTPException(status_code=503, detail="Frontend build ontbreekt")

    return FileResponse(index_file)
