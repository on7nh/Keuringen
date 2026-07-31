# API-ontwerp Toestellenmodule

## Digitaal Keurings- en Documentbeheer

**Documentnummer:** 11  
**Versie:** 1.0 Concept  
**Gerelateerd:** `05_API_Ontwerp.md`, `09_Toestellen_En_Onderhoudsbeheer.md`, `10_Database_Ontwerp_Toestellen.md`

## 1. Doel

Dit document beschrijft de REST API voor registratie, classificatie, QR-resolutie, onderhoud, storingen, herstellingen, keuringen, documenten, dashboards en rapportering van toestellen.

## 2. Algemene principes

- Basisroute: `/api/v1`.
- JSON als standaard payloadformaat.
- UTF-8.
- Datums volgens ISO 8601.
- Tijden in UTC met tijdzone-informatie.
- JWT-authenticatie voor aangemelde gebruikers.
- Sterke authenticatie en step-up authenticatie voor gevoelige acties.
- Tenant- en sitescoping wordt in de backend afgedwongen.
- Idempotency keys voor kritieke POST-acties.
- Cursorpaginering voor grote lijsten.
- OpenAPI is de contractuele bron.

## 3. Resourcebenaming

Belangrijkste resources:

- `assets`
- `asset-types`
- `asset-categories`
- `asset-brands`
- `asset-models`
- `asset-qr-labels`
- `maintenance-plans`
- `maintenance-tasks`
- `faults`
- `repairs`
- `inspections`
- `asset-documents`
- `asset-reports`

## 4. Standaard headers

```text
Authorization: Bearer <jwt>
Content-Type: application/json
Accept: application/json
X-Correlation-ID: <uuid>
Idempotency-Key: <uuid>
```

`Idempotency-Key` is verplicht voor acties die dubbele registraties kunnen veroorzaken, zoals onderhoud bevestigen, storing melden, herstelling afsluiten en QR-labels genereren.

## 5. Standaard responsevorm

```json
{
  "data": {},
  "meta": {
    "correlation_id": "9caa64ec-a10e-43a8-b018-3410e66df5f1",
    "timestamp": "2026-07-31T06:00:00Z"
  }
}
```

Lijstresponse:

```json
{
  "data": [],
  "meta": {
    "next_cursor": "eyJpZCI6IjEyMyJ9",
    "has_more": true,
    "total_estimate": 14520
  }
}
```

## 6. Foutmodel

```json
{
  "error": {
    "code": "ASSET_NOT_FOUND",
    "message": "Het toestel bestaat niet of is niet toegankelijk.",
    "details": {},
    "correlation_id": "9caa64ec-a10e-43a8-b018-3410e66df5f1"
  }
}
```

Belangrijke foutcodes:

- `VALIDATION_ERROR`
- `UNAUTHORIZED`
- `FORBIDDEN`
- `STEP_UP_REQUIRED`
- `ASSET_NOT_FOUND`
- `ASSET_CODE_CONFLICT`
- `SERIAL_NUMBER_CONFLICT`
- `INVALID_SITE_SCOPE`
- `QR_TOKEN_INVALID`
- `QR_TOKEN_REVOKED`
- `MAINTENANCE_TASK_CONFLICT`
- `FAULT_ALREADY_CLOSED`
- `INSPECTION_RESULT_INVALID`
- `DOCUMENT_ACCESS_DENIED`
- `RATE_LIMITED`

## 7. Autorisatiescopes

Voorbeelden:

- `assets.read`
- `assets.create`
- `assets.update`
- `assets.archive`
- `assets.move`
- `assets.qr.manage`
- `maintenance.read`
- `maintenance.execute`
- `maintenance.confirm`
- `faults.create`
- `faults.manage`
- `repairs.manage`
- `inspections.manage`
- `asset_documents.manage`
- `asset_reports.read`
- `asset_reports.export`

## 8. Stamgegevens-API

### 8.1 Merken

```text
GET    /api/v1/asset-brands
POST   /api/v1/asset-brands
GET    /api/v1/asset-brands/{brand_id}
PATCH  /api/v1/asset-brands/{brand_id}
DELETE /api/v1/asset-brands/{brand_id}
```

`DELETE` deactiveert standaard en verwijdert niet fysiek wanneer het merk in gebruik is.

### 8.2 Soorten

```text
GET    /api/v1/asset-types
POST   /api/v1/asset-types
GET    /api/v1/asset-types/{type_id}
PATCH  /api/v1/asset-types/{type_id}
DELETE /api/v1/asset-types/{type_id}
```

### 8.3 Categorieën

```text
GET    /api/v1/asset-categories
POST   /api/v1/asset-categories
GET    /api/v1/asset-categories/{category_id}
PATCH  /api/v1/asset-categories/{category_id}
DELETE /api/v1/asset-categories/{category_id}
GET    /api/v1/asset-categories/tree
```

### 8.4 Modellen

```text
GET    /api/v1/asset-models
POST   /api/v1/asset-models
GET    /api/v1/asset-models/{model_id}
PATCH  /api/v1/asset-models/{model_id}
DELETE /api/v1/asset-models/{model_id}
```

## 9. Toestellen-API

### 9.1 Lijst

```text
GET /api/v1/assets
```

Filters:

- `organization_id`
- `site_id`
- `building_id`
- `room_id`
- `asset_type_id`
- `category_id`
- `brand_id`
- `model_id`
- `status`
- `criticality`
- `warranty_state`
- `maintenance_due_before`
- `inspection_due_before`
- `has_open_faults`
- `q`
- `cursor`
- `limit`
- `sort`

### 9.2 Aanmaken

```text
POST /api/v1/assets
```

Voorbeeld:

```json
{
  "organization_id": "org_123",
  "site_id": "site_456",
  "asset_type_id": "type_1",
  "asset_category_id": "cat_1",
  "brand_id": "brand_1",
  "model_id": "model_1",
  "display_name": "Koelcel keuken 1",
  "serial_number": "SN-2024-00189",
  "criticality": "high",
  "commissioned_at": "2024-03-15",
  "generate_qr_label": true
}
```

Response bevat het toegekende `asset_code` en, wanneer gevraagd, een éénmalig beschikbare QR-token of labelreferentie.

### 9.3 Detail en wijziging

```text
GET   /api/v1/assets/{asset_id}
PATCH /api/v1/assets/{asset_id}
```

PATCH gebruikt JSON Merge Patch. Onveranderlijke velden zoals `asset_code` worden geweigerd.

### 9.4 Archiveren

```text
POST /api/v1/assets/{asset_id}/archive
```

Payload:

```json
{
  "reason": "Toestel definitief verwijderd uit inventaris",
  "effective_at": "2026-07-31T06:00:00Z"
}
```

### 9.5 Verplaatsen

```text
POST /api/v1/assets/{asset_id}/move
```

Payload bevat nieuwe site- en locatievelden, reden en ingangsdatum.

### 9.6 Tijdlijn

```text
GET /api/v1/assets/{asset_id}/timeline
```

Ondersteunt filters op gebeurtenistype, datumperiode en gerelateerde entiteit.

### 9.7 Samenvatting

```text
GET /api/v1/assets/{asset_id}/summary
```

Levert compacte data voor de landingspagina: status, locatie, open storingen, volgende onderhouds- en keuringsdatum.

## 10. QR-API

### 10.1 Label genereren

```text
POST /api/v1/assets/{asset_id}/qr-labels
```

```json
{
  "label_type": "primary",
  "format": "50x30mm",
  "include_site_name": true
}
```

### 10.2 Labels opvragen

```text
GET /api/v1/assets/{asset_id}/qr-labels
```

### 10.3 Label intrekken

```text
POST /api/v1/assets/{asset_id}/qr-labels/{label_id}/revoke
```

### 10.4 Publieke resolver

```text
GET /q/{token}
```

Flow:

1. Token normaliseren.
2. Hash berekenen.
3. Actief label zoeken.
4. Rate limit toepassen.
5. Scanstatistiek asynchroon registreren.
6. Redirect naar canonical toestelroute.
7. Autorisatie bepalen op de bestemmingspagina.

Mogelijke responses:

- `302 Found` naar toestelpagina;
- `404` bij onbekende token;
- `410 Gone` bij ingetrokken label;
- `429 Too Many Requests` bij misbruik.

## 11. Onderhoudsplannen

```text
GET    /api/v1/maintenance-plans
POST   /api/v1/maintenance-plans
GET    /api/v1/maintenance-plans/{plan_id}
PATCH  /api/v1/maintenance-plans/{plan_id}
DELETE /api/v1/maintenance-plans/{plan_id}
POST   /api/v1/maintenance-plans/{plan_id}/assign-assets
```

## 12. Onderhoudstaken

```text
GET    /api/v1/maintenance-tasks
POST   /api/v1/assets/{asset_id}/maintenance-tasks
GET    /api/v1/maintenance-tasks/{task_id}
PATCH  /api/v1/maintenance-tasks/{task_id}
POST   /api/v1/maintenance-tasks/{task_id}/assign
POST   /api/v1/maintenance-tasks/{task_id}/start
POST   /api/v1/maintenance-tasks/{task_id}/complete
POST   /api/v1/maintenance-tasks/{task_id}/confirm
POST   /api/v1/maintenance-tasks/{task_id}/cancel
```

Bevestigingspayload:

```json
{
  "result": "completed",
  "completed_at": "2026-07-31T05:45:00Z",
  "checklist": [
    {"item_code": "FILTER", "result": "ok"},
    {"item_code": "TEMP", "result": "ok", "value": 3.8, "unit": "C"}
  ],
  "notes": "Onderhoud uitgevoerd zonder opmerkingen",
  "next_due_at": "2027-01-31T00:00:00Z",
  "document_ids": ["doc_123"]
}
```

## 13. Storingen

```text
GET    /api/v1/assets/{asset_id}/faults
POST   /api/v1/assets/{asset_id}/faults
GET    /api/v1/faults/{fault_id}
PATCH  /api/v1/faults/{fault_id}
POST   /api/v1/faults/{fault_id}/triage
POST   /api/v1/faults/{fault_id}/assign
POST   /api/v1/faults/{fault_id}/resolve
POST   /api/v1/faults/{fault_id}/close
POST   /api/v1/faults/{fault_id}/reopen
```

Publieke beperkte meldroute:

```text
POST /api/v1/public/assets/{public_asset_ref}/fault-reports
```

Deze route vereist CAPTCHA of gelijkwaardige misbruikbeperking, rate limiting en minimale gegevensverwerking.

## 14. Herstellingen

```text
GET    /api/v1/assets/{asset_id}/repairs
POST   /api/v1/assets/{asset_id}/repairs
GET    /api/v1/repairs/{repair_id}
PATCH  /api/v1/repairs/{repair_id}
POST   /api/v1/repairs/{repair_id}/add-part
POST   /api/v1/repairs/{repair_id}/complete
POST   /api/v1/repairs/{repair_id}/reopen
```

Een herstelling kan via `fault_ids` aan meerdere storingen worden gekoppeld.

## 15. Keuringen

```text
GET    /api/v1/assets/{asset_id}/inspections
POST   /api/v1/assets/{asset_id}/inspections
GET    /api/v1/inspections/{inspection_id}
PATCH  /api/v1/inspections/{inspection_id}
POST   /api/v1/inspections/{inspection_id}/finalize
POST   /api/v1/inspections/{inspection_id}/add-finding
POST   /api/v1/inspection-findings/{finding_id}/resolve
```

Bij resultaat `rejected` kan de API automatisch een statuswijziging en corrigerende actie creëren.

## 16. Documenten en media

```text
GET    /api/v1/assets/{asset_id}/documents
POST   /api/v1/assets/{asset_id}/documents
PATCH  /api/v1/assets/{asset_id}/documents/{link_id}
DELETE /api/v1/assets/{asset_id}/documents/{link_id}
POST   /api/v1/assets/{asset_id}/photos
```

Upload gebeurt via de bestaande documentuploadflow. De toestel-API ontvangt daarna een `document_id` en koppelt dit aan het toestel.

## 17. Dashboards en rapporten

```text
GET /api/v1/asset-reports/overview
GET /api/v1/asset-reports/faults
GET /api/v1/asset-reports/reliability
GET /api/v1/asset-reports/maintenance-compliance
GET /api/v1/asset-reports/inspection-compliance
GET /api/v1/asset-reports/costs
GET /api/v1/asset-reports/site-comparison
GET /api/v1/asset-reports/replacement-forecast
POST /api/v1/asset-reports/exports
```

### 17.1 Toestelstatistieken

```text
GET /api/v1/assets/{asset_id}/statistics?from=2021-01-01&to=2025-12-31
```

Response:

```json
{
  "data": {
    "fault_count": 12,
    "repair_count": 10,
    "maintenance_count": 18,
    "inspection_count": 5,
    "downtime_minutes": 8460,
    "mttr_minutes": 846,
    "mtbf_hours": 3120,
    "maintenance_cost": 4200.50,
    "repair_cost": 7850.00
  }
}
```

## 18. Exporttaken

Grote exports zijn asynchroon:

```text
POST /api/v1/asset-reports/exports
GET  /api/v1/asset-reports/exports/{export_id}
GET  /api/v1/asset-reports/exports/{export_id}/download
```

Statussen: `queued`, `running`, `completed`, `failed`, `expired`.

## 19. Batch-API

```text
POST /api/v1/assets/batch/move
POST /api/v1/assets/batch/archive
POST /api/v1/assets/batch/assign-maintenance-plan
POST /api/v1/assets/batch/assign-inspection-plan
POST /api/v1/assets/batch/generate-qr-labels
```

Elke batchactie ondersteunt `dry_run=true` en levert vooraf impact en validatiefouten.

## 20. Import-API

```text
POST /api/v1/asset-imports
POST /api/v1/asset-imports/{import_id}/map-columns
POST /api/v1/asset-imports/{import_id}/validate
POST /api/v1/asset-imports/{import_id}/simulate
POST /api/v1/asset-imports/{import_id}/execute
GET  /api/v1/asset-imports/{import_id}
GET  /api/v1/asset-imports/{import_id}/errors
```

## 21. Webhooks en integraties

Interne eventtopics:

- `asset.created`
- `asset.updated`
- `asset.moved`
- `asset.status_changed`
- `asset.qr_scanned`
- `maintenance.due`
- `maintenance.completed`
- `fault.reported`
- `fault.resolved`
- `repair.completed`
- `inspection.expiring`
- `inspection.rejected`

Uitgaande webhooks worden ondertekend met HMAC en bevatten replay-bescherming.

## 22. Rate limiting

Aanbevolen limieten:

- QR-resolver: per IP en tokenprefix.
- Publieke storing melden: streng per IP en toestel.
- Rapporten: per gebruiker en organisatie.
- Exports: maximaal aantal gelijktijdige taken.
- Batchacties: alleen voor bevoegde rollen.

## 23. Concurrency

Mutaties ondersteunen `ETag` en `If-Match` voor optimistic locking.

Bij mismatch:

```text
409 Conflict
```

met code `RESOURCE_VERSION_CONFLICT`.

## 24. Audit

Elke muterende endpoint registreert:

- gebruiker of technische actor;
- organisatie;
- site;
- resource en resource-id;
- oude en nieuwe waarden waar toegestaan;
- correlation-id;
- IP-adres volgens privacybeleid;
- resultaat;
- tijdstip.

## 25. OpenAPI-organisatie

Aanbevolen tags:

- Asset Brands
- Asset Types
- Asset Categories
- Asset Models
- Assets
- QR Labels
- Maintenance Plans
- Maintenance Tasks
- Faults
- Repairs
- Inspections
- Asset Documents
- Asset Reports
- Asset Imports

## 26. Acceptatiecriteria

- Alle endpoints zijn in OpenAPI beschreven.
- Elke endpoint heeft scopecontrole.
- Organisatie- en sitescoping is getest.
- QR-resolver lekt geen interne identifiers.
- Idempotency voorkomt dubbele transacties.
- Grote exports zijn asynchroon.
- Mutaties zijn auditbaar.
- Foutcodes zijn stabiel en gedocumenteerd.
- Rapportdefinities stemmen overeen met het database- en AI-ontwerp.
