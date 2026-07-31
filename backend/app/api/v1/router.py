from fastapi import APIRouter

from app.api.v1 import ai, auth, documents, inspections, organizations, system

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(organizations.router)
api_router.include_router(documents.router)
api_router.include_router(inspections.router)
api_router.include_router(system.router)
api_router.include_router(ai.router)
