from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_permission
from app.core.database import get_db
from app.models.organization import Discipline, Installation, InstallationType, Organization, Site
from app.models.documents import DocumentType
from app.schemas.organization import (
    DisciplineOut,
    DisciplineUpsert,
    DocumentTypeOut,
    DocumentTypeUpsert,
    OrganizationCreate,
    OrganizationOut,
    OrganizationUpdate,
    SiteCreate,
    SiteOut,
    SiteUpdate,
)
from app.services.organization_service import allocate_storage_code, next_temporary_site_number

router = APIRouter(tags=["organizations"])


@router.get("/organizations", response_model=list[OrganizationOut])
def list_organizations(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(Organization).filter(Organization.deleted_at.is_(None)).all()


@router.post(
    "/organizations",
    response_model=OrganizationOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("organizations.manage"))],
)
def create_organization(payload: OrganizationCreate, db: Session = Depends(get_db)):
    org = Organization(**payload.model_dump())
    db.add(org)
    db.commit()
    db.refresh(org)
    return org


@router.get("/organizations/{organization_id}", response_model=OrganizationOut)
def get_organization(organization_id: uuid.UUID, db: Session = Depends(get_db), _=Depends(get_current_user)):
    org = db.get(Organization, organization_id)
    if org is None or org.deleted_at is not None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Organization not found")
    return org


@router.patch(
    "/organizations/{organization_id}",
    response_model=OrganizationOut,
    dependencies=[Depends(require_permission("organizations.manage"))],
)
def update_organization(organization_id: uuid.UUID, payload: OrganizationUpdate, db: Session = Depends(get_db)):
    org = db.get(Organization, organization_id)
    if org is None or org.deleted_at is not None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Organization not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(org, field, value)
    db.commit()
    db.refresh(org)
    return org


@router.get("/sites", response_model=list[SiteOut])
def list_sites(
    organization_id: uuid.UUID | None = None,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    query = db.query(Site).filter(Site.deleted_at.is_(None))
    if organization_id:
        query = query.filter(Site.organization_id == organization_id)
    return query.all()


@router.post(
    "/sites",
    response_model=SiteOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("sites.manage"))],
)
def create_site(payload: SiteCreate, db: Session = Depends(get_db)):
    storage_code = allocate_storage_code(db)
    is_temporary = payload.site_number is None
    site_number = payload.site_number or next_temporary_site_number(db, payload.organization_id)

    site = Site(
        organization_id=payload.organization_id,
        site_number=site_number,
        code=payload.code,
        name=payload.name,
        storage_code=storage_code,
        storage_relative_path=storage_code,
        is_temporary_site_number=is_temporary,
        address_street=payload.address_street,
        address_number=payload.address_number,
        address_postal_code=payload.address_postal_code,
        address_city=payload.address_city,
        address_country=payload.address_country,
        timezone=payload.timezone,
    )
    db.add(site)
    db.commit()
    db.refresh(site)
    return site


@router.get("/sites/{site_id}", response_model=SiteOut)
def get_site(site_id: uuid.UUID, db: Session = Depends(get_db), _=Depends(get_current_user)):
    site = db.get(Site, site_id)
    if site is None or site.deleted_at is not None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Site not found")
    return site


@router.patch(
    "/sites/{site_id}",
    response_model=SiteOut,
    dependencies=[Depends(require_permission("sites.manage"))],
)
def update_site(site_id: uuid.UUID, payload: SiteUpdate, db: Session = Depends(get_db)):
    site = db.get(Site, site_id)
    if site is None or site.deleted_at is not None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Site not found")

    data = payload.model_dump(exclude_unset=True)
    if "site_number" in data and data["site_number"]:
        # Assigning a definitive site number - the physical storage folder
        # (storage_code / storage_relative_path) never changes, per docs/02
        # section 6.3.6. A full filename migration of existing documents
        # would run as a separate background job (not yet implemented).
        site.is_temporary_site_number = False
    for field, value in data.items():
        setattr(site, field, value)
    db.commit()
    db.refresh(site)
    return site


@router.get("/disciplines", response_model=list[DisciplineOut])
def list_disciplines(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(Discipline).filter(Discipline.is_active.is_(True)).all()


@router.post(
    "/disciplines",
    response_model=DisciplineOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("settings.manage"))],
)
def upsert_discipline(payload: DisciplineUpsert, db: Session = Depends(get_db)):
    discipline = db.query(Discipline).filter(Discipline.code == payload.code).first()
    if discipline is None:
        discipline = Discipline(code=payload.code)
        db.add(discipline)
    discipline.name = payload.name
    discipline.validity_value = payload.validity_value
    discipline.validity_unit = payload.validity_unit
    discipline.is_general = payload.is_general
    db.commit()
    db.refresh(discipline)
    return discipline


@router.get("/document-types", response_model=list[DocumentTypeOut])
def list_document_types(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(DocumentType).all()


@router.post(
    "/document-types",
    response_model=DocumentTypeOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("settings.manage"))],
)
def upsert_document_type(payload: DocumentTypeUpsert, db: Session = Depends(get_db)):
    document_type = db.query(DocumentType).filter(DocumentType.code == payload.code).first()
    if document_type is None:
        document_type = DocumentType(code=payload.code)
        db.add(document_type)
    document_type.name = payload.name
    document_type.requires_inspection_data = payload.requires_inspection_data
    document_type.supports_ai_analysis = payload.supports_ai_analysis
    db.commit()
    db.refresh(document_type)
    return document_type
