from __future__ import annotations

import uuid

from pydantic import BaseModel, Field


class OrganizationCreate(BaseModel):
    code: str = Field(max_length=32)
    name: str
    sharepoint_marking_enabled: bool = False
    default_timezone: str = "Europe/Brussels"


class OrganizationUpdate(BaseModel):
    name: str | None = None
    is_active: bool | None = None
    sharepoint_marking_enabled: bool | None = None
    default_timezone: str | None = None


class OrganizationOut(BaseModel):
    id: uuid.UUID
    code: str
    name: str
    is_active: bool
    sharepoint_marking_enabled: bool
    default_timezone: str

    model_config = {"from_attributes": True}


class SiteCreate(BaseModel):
    organization_id: uuid.UUID
    site_number: str | None = None
    code: str
    name: str
    address_street: str | None = None
    address_number: str | None = None
    address_postal_code: str | None = None
    address_city: str | None = None
    address_country: str | None = None
    timezone: str = "Europe/Brussels"


class SiteUpdate(BaseModel):
    name: str | None = None
    site_number: str | None = None
    address_street: str | None = None
    address_number: str | None = None
    address_postal_code: str | None = None
    address_city: str | None = None
    address_country: str | None = None
    is_active: bool | None = None


class SiteOut(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    site_number: str
    code: str
    name: str
    storage_code: str
    is_temporary_site_number: bool
    is_active: bool

    model_config = {"from_attributes": True}


class DisciplineOut(BaseModel):
    id: uuid.UUID
    code: str
    name: str
    validity_value: int | None
    validity_unit: str | None
    is_general: bool
    is_active: bool

    model_config = {"from_attributes": True}


class DisciplineUpsert(BaseModel):
    code: str
    name: str
    validity_value: int | None = None
    validity_unit: str | None = None
    is_general: bool = False


class DocumentTypeOut(BaseModel):
    id: uuid.UUID
    code: str
    name: str
    requires_inspection_data: bool
    supports_ai_analysis: bool

    model_config = {"from_attributes": True}


class DocumentTypeUpsert(BaseModel):
    code: str
    name: str
    requires_inspection_data: bool = False
    supports_ai_analysis: bool = True
