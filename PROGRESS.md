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
- **Beheer (Admin) scherm** — organisaties, disciplines en documenttypes
  aanmaken vanuit de UI (voorheen alleen via de API).
- **Systeemstatus scherm** — `GET /api/v1/system/status` toont PostgreSQL-,
  Redis- en documentopslag-bereikbaarheid (met schrijftest en vrije ruimte),
  plus een alleen-lezen software-updatecheck die het draaiende commit
  vergelijkt met de laatste commit op de gevolgde branch (via een read-only
  bind mount van de repository + `git ls-remote`, geen Docker-socket-
  toegang). De update-check toont enkel het exacte commando om handmatig
  te updaten; er is bewust geen "1-klik herstart"-knop gebouwd, aangezien
  dat de webcontainer toegang tot de Docker-daemon van de host zou moeten
  geven — een aanzienlijke uitbreiding van het aanvalsoppervlak die niet
  stilzwijgend wordt toegevoegd.
- **Infrastructuur** — Dockerfile (multi-stage: React-build + FastAPI-image),
  `docker-compose.yml` conform docs/20 (web/worker/scheduler/redis, één
  gepubliceerde poort), `docker-compose.override.yml` met een lokale
  PostgreSQL-container voor ontwikkeling, Alembic-migraties (geverifieerd:
  volledige upgrade/downgrade-cyclus zonder schema drift).
- **Beveiliging en aanmelden-scherm** (docs/07 §18) — volledig zelfbedieningsscherm
  voor Passkeys (toevoegen, hernoemen, intrekken), TOTP (instellen, bevestigen,
  verwijderen), herstelcodes (genereren, eenmalig tonen) en actieve sessies
  (overzicht met "huidige sessie"-badge, individueel of gezamenlijk beëindigen).
  Blokkeert het verwijderen van de laatste actieve methode in de UI zelf
  (naast de bestaande backend-validatie).
- **Step-up-authenticatiemodal** (docs/07 §19) — herbruikbare React-context
  (`useStepUp`/`withStepUp`) die een `STEP_UP_REQUIRED`-fout opvangt, Passkey
  of TOTP-bevestiging toont, en de oorspronkelijke actie automatisch hervat
  na succes.
- **Wizard voor eerste sterke-authenticatie-instelling** (docs/07 §5.6,
  vereenvoudigd) — niet-wegklikbare banner op elke pagina wanneer sterke
  authenticatie verplicht is maar nog geen methode is geregistreerd, met
  directe link naar het beveiligingsscherm.
- **Meertaligheidsbasis** (docs/07 §8) — `LanguageContext` met nl/en-
  woordenboeken, automatische taaldetectie via de browser, taalkeuze in
  navigatie en aanmeldscherm. Dekt vooralsnog navigatie, aanmeldscherm en
  gemeenschappelijke acties; de overige schermen zijn nog niet vertaald
  (zie "Bekende vereenvoudigingen").
- **"Problemen met aanmelden?"-link** op het aanmeldscherm (docs/07 §5.2).

Tijdens het bouwen van het beveiligingsscherm zijn drie reële fouten in de
eerder gebouwde authenticatielaag gevonden en gecorrigeerd (bevestigd met
een browsertest, niet alleen code-inspectie):

1. `POST /auth/step-up/options` genereerde voor Passkey-stap-up nooit een
   echte WebAuthn-challenge — elke Passkey-stap-up zou hebben gefaald.
   Losgemaakt van de (wel correct werkende) inlogflow via een nieuwe
   `build_step_up_options`.
2. `GET /auth/sessions` crashte met een 500 zodra er sessies met een
   IP-adres bestonden: psycopg geeft `ipaddress.IPv4Address` terug voor
   `INET`-kolommen, wat Pydantic's `str`-veld niet accepteerde.
3. `POST /auth/logout-all` trok ook de sessie van de aanroeper zelf in,
   in plaats van alleen "alle *andere* sessies" zoals de spec vereist.

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
- **Toestellen- en Onderhoudsbeheer** (docs/09–13) — een volledig tweede
  module (toestelregistratie, QR-codes, onderhoud, storingen, herstellingen,
  toestelkeuringen, MTTR/MTBF-rapportage, plus een eigen AI-analytics-laag
  voor predictive maintenance). Nog niet gestart; qua omvang vergelijkbaar
  met alles wat tot nu toe gebouwd is.

## Bekende vereenvoudigingen t.o.v. de spec

- De uploadflow is één synchrone multipart-aanroep
  (`POST /documents/upload`) in plaats van de drieledige
  `POST /uploads` → `PUT /uploads/{id}/content` → `POST /uploads/{id}/complete`
  uit `docs/05`. Chunked upload stond daar zelf al als open ontwerpbeslissing.
  Voor bestanden tot 100 MB werkt de huidige aanpak betrouwbaar (getest).
- Malware-scanning is een placeholder-status (`SKIPPED`); er is geen
  scanner aangesloten.
- De NAS-koppeling is en blijft een hostniveau-instelling (NFS/SMB-mount
  naar `DOCUMENT_STORAGE_PATH`, per docs/20 §12), niet iets dat via de
  applicatie met opslaggegevens/credentials wordt geconfigureerd. Het
  Systeemstatus-scherm maakt een gebroken of ontbrekende mount zichtbaar
  (met pad en foutmelding) zodat die op de host kan worden opgelost.
- De "eerste registratie"-wizard uit docs/07 §5.6 is vereenvoudigd tot een
  niet-wegklikbare banner die naar het bestaande beveiligingsscherm linkt,
  in plaats van een aparte stapsgewijze wizard-flow.
- Meertaligheid dekt vooralsnog navigatie, aanmeldscherm en de kopteksten
  van het beveiligingsscherm. Sites, Documenten, Keuringen, Beheer en
  Systeemstatus tonen nog uitsluitend Nederlandse tekst — de architectuur
  (`LanguageContext`, woordenboeken per taal) is aanwezig om dit
  schermgewijs uit te breiden.
