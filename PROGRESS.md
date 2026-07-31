# Implementatiestatus

Dit document geeft een eerlijk overzicht van wat in deze eerste iteratie is
gebouwd, getest en werkend bevonden, en wat nog open staat. De volledige
specificatie staat in [`docs/`](docs/); deze iteratie volgt de
"Initiële implementatievolgorde" uit
[`docs/03_Database_Ontwerp.md`](docs/03_Database_Ontwerp.md) (punten 1–6).

## Geïmplementeerd en getest

- **Gebruikers, rollen en autorisatie** — `users`, `roles`, `permissions`,
  organisatie-/sitegebonden rollen, RBAC-dependency in de API.
- **Sterke authenticatie** — wachtwoord + TOTP, WebAuthn/Passkeys
  (registratie en login), eenmalige herstelcodes, step-up-authenticatie,
  sessies met refresh-tokenrotatie en intrekking, security-auditlog
  (`authentication_events`). Geverifieerd met een echte browser-passkey-flow
  is niet mogelijk zonder een fysieke/virtuele authenticator, maar de
  wachtwoord+TOTP-flow is end-to-end getest (API en browser).
- **Organisaties, Sites en referentiegegevens** — CRUD, tijdelijke
  `TMPnnn`-sitenummers, onveranderlijke `storage_code` per Site (docs/02
  §6.3.4–6.3.5), disciplines met configureerbare vervaltermijn,
  documenttypes.
- **Documentbeheer** — upload met validatie (bestandstype, 100 MB-limiet,
  SHA-256-hash, duplicaatdetectie), centrale `NamingService` die de
  bestandsnaamconventie afdwingt (`Site_Sitenummer_Discipline_Type_Datum.ext`,
  volgnummer bij conflict), one-file-at-a-time verwerking per Site via een
  Postgres advisory lock, documentversies, optimistic locking (`row_version`).
- **Keuringsbeheer** — `inspection_reports` met verplichte UNCONFIRMED-status
  vóór definitieve validatie, automatische vervaldatumberekening
  (`inspectiedatum + vervaltermijn van de discipline`), `inspection_schedules`
  voor de "binnenkort vervallen"-lijst, findings.
- **Frontend** — React/TypeScript/Vite, aanmeldscherm (wachtwoord+TOTP en
  passkey), dashboard met vervaloverzicht, Sites-, Documenten- en
  Keuringenschermen, geïntegreerd geserveerd via FastAPI (één image, poort
  8080, per docs/20).
- **Infrastructuur** — Dockerfile (multi-stage: React-build + FastAPI-image),
  `docker-compose.yml` conform docs/20 (web/worker/scheduler/redis, één
  gepubliceerde poort), `docker-compose.override.yml` met een lokale
  PostgreSQL-container voor ontwikkeling, Alembic-migraties (geverifieerd:
  volledige upgrade/downgrade-cyclus zonder schema drift).

## Bewust nog niet gebouwd

Deze onderdelen staan wel in de specificatie maar zijn in deze iteratie
overgeslagen om een samenhangende, geteste kernstroom op te leveren in
plaats van veel losse, ongeteste fragmenten:

- **AI-verwerking** (OCR, Vision, LLM-analyse, promptbeheer, modelbeheer) —
  `docs/04` en `docs/02` §5. Er staat een `app/workers/ai_jobs.py`-scaffold
  klaar die expliciet `NotImplementedError` opwerpt; er is geen aansluiting
  op een echte AI-server.
- **Menselijke correcties / feedbackregistratie** voor het verbeteren van
  AI-herkenning (`ai_feedback`, kwaliteitsscherm) — hangt af van AI-verwerking.
- **Kennisbank / RAG** (`knowledge_entities`, `knowledge_rules`,
  `knowledge_chunks`, embeddings, pgvector) — `docs/04`.
- **Fotoverwerking in batch** (`photo_batches`, EXIF-datumherkenning,
  batchbevestiging) — `docs/01` §Fotoverwerking.
- **Sitemigratie** bij toekenning van een definitief sitenummer (het
  gecontroleerde, hervatbare hernoemproces uit docs/02 §6.3.6–6.3.9) — het
  datamodel (`is_temporary_site_number`, onveranderlijke `storage_code`)
  ondersteunt dit al; het `PATCH /sites/{id}`-endpoint wijzigt vandaag alleen
  de functionele metadata, zonder de bestanden effectief te hernoemen.
- **E-mail/notificaties** (`email_queue`, `notifications`,
  `reminder_policies`, inbox `keuringen@elecon.be`) — de
  reminder-Celery-task telt vandaag alleen vervallende keuringen, verstuurt
  niets.
- **Rapportering/exports** (`GET /reports/...`, Excel-import/export).
- **SharePoint-markering** (eenvoudig te bouwen, maar nog niet gedaan).
- **Realtime gebeurtenissen** (SSE `/events`).
- **Risicoanalyse-module** (`risk_analyses`, `risk_items`) — geen modellen of
  endpoints.
- Uitgebreide RBAC-scoping op site-/organisatieniveau: `require_permission`
  controleert vandaag alleen systeembrede permissies via rollen, niet of de
  gebruiker specifiek toegang heeft tot de betrokken organisatie of Site.
  Voor productiegebruik moet dit nog verder afgedwongen worden per endpoint.

## Bekende vereenvoudigingen t.o.v. de spec

- De uploadflow is één synchrone multipart-aanroep
  (`POST /documents/upload`) in plaats van de drieledige
  `POST /uploads` → `PUT /uploads/{id}/content` → `POST /uploads/{id}/complete`
  uit `docs/05`. Chunked upload stond daar zelf al als open ontwerpbeslissing.
  Voor bestanden tot 100 MB werkt de huidige aanpak betrouwbaar (getest).
- Malware-scanning is een placeholder-status (`SKIPPED`); er is geen
  scanner aangesloten.
