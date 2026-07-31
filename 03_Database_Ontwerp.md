# Database Ontwerp

## Digitaal Keurings- en Documentbeheer

**Versie:** 1.1 Concept  
**Status:** Uitgewerkt logisch en fysiek ontwerp

## 1. Doel

Dit document beschrijft de logische en fysieke opbouw van de PostgreSQL-database. De database is de centrale bron van waarheid voor organisaties, sites, documenten, keuringen, gebruikers, sterke authenticatie, AI-verwerking, menselijke correcties, kennisregels, auditgegevens en configuratie.

Bestanden, modelbestanden en grote binaire objecten worden niet als primaire inhoud in PostgreSQL opgeslagen. De database registreert hun locatie, technische eigenschappen, versie en integriteit.

## 2. Ontwerpprincipes

- PostgreSQL als primaire relationele database
- UUID's als primaire sleutels
- UTC voor technische tijdstippen; lokale tijdzone alleen voor presentatie
- Normalisatie waar dit beheerbaarheid en gegevenskwaliteit verbetert
- JSONB alleen voor variabele technische metadata en ruwe AI-resultaten
- Soft delete voor bedrijfsobjecten die historisch raadpleegbaar moeten blijven
- Onveranderbare auditregistratie voor kritieke acties
- Optimistic locking via een versienummer of `updated_at`
- Bestanden op de Synology NAS; alleen metadata in PostgreSQL
- Volledige herleidbaarheid van AI-voorstel naar gebruikersbeslissing
- Voorbereiding op pgvector voor lokale semantische zoeking
- Schemawijzigingen uitsluitend via Alembic-migraties
- Meerdere sterke authenticatiemethoden per gebruiker
- WebAuthn-credentials bevatten uitsluitend publieke sleutelgegevens; private sleutels en biometrische gegevens worden nooit opgeslagen
- Herstelcodes worden uitsluitend gehasht opgeslagen
- TOTP-geheimen worden versleuteld opgeslagen en nooit gelogd

## 3. Database-extensies

Voorziene extensies:

```sql
CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS citext;
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE EXTENSION IF NOT EXISTS vector;
```

`vector` wordt pas in productie geactiveerd wanneer pgvector als definitieve keuze is bevestigd.

## 4. Naamgevingsconventies

- Tabellen en kolommen: `snake_case`
- Tabellen: meervoud
- Primaire sleutel: `id`
- Foreign key: `<entiteit>_id`
- Tijdstippen: `<actie>_at`
- Gebruikersreferentie: `<actie>_by`
- Booleans: `is_...` of `has_...`
- Unieke constraints: `uq_<tabel>_<kolommen>`
- Foreign keys: `fk_<tabel>_<kolom>_<doeltabel>`
- Indexen: `ix_<tabel>_<kolommen>`

## 5. Gemeenschappelijke kolommen

Belangrijke bedrijfsentiteiten bevatten minimaal:

```text
id UUID PRIMARY KEY
created_at TIMESTAMPTZ NOT NULL
created_by UUID NULL
updated_at TIMESTAMPTZ NOT NULL
updated_by UUID NULL
deleted_at TIMESTAMPTZ NULL
deleted_by UUID NULL
row_version INTEGER NOT NULL DEFAULT 1
```

Referentietabellen kunnen een eenvoudiger auditmodel gebruiken.

## 6. Hoofdmodel

```text
Organization
  +-- Sites
       +-- Installations
       +-- Documents
       |    +-- DocumentVersions
       |    +-- DocumentFields
       |    +-- AIJobs
       |    +-- AIFeedback
       |    +-- KnowledgeSources
       +-- InspectionReports
       +-- RiskAnalyses
       +-- Photos

Users
  +-- UserOrganizationRoles
  +-- UserSiteRoles
  +-- UserAuthenticationMethods
  +-- UserPasskeys
  +-- UserTotpConfigurations
  +-- RecoveryCodes
  +-- UserSessions
  +-- AuthenticationEvents

AIModels
  +-- ModelVersions
  +-- Prompts
  +-- PromptVersions
  +-- AIJobs

KnowledgeEntities
  +-- KnowledgeRelations
  +-- KnowledgeAliases
  +-- KnowledgeChunks / Embeddings
```

## 7. Identiteit, sterke authenticatie en autorisatie

### 7.1 `users`

Belangrijkste kolommen:

- `id`
- `email CITEXT UNIQUE NOT NULL`
- `display_name`
- `password_hash NULL`
- `is_active`
- `is_system_admin`
- `preferred_authentication_method NULL`
- `strong_authentication_required`
- `passwordless_enabled`
- `last_login_at NULL`
- `failed_login_count`
- `locked_until NULL`
- `credentials_changed_at NULL`

`password_hash` mag alleen `NULL` zijn wanneer wachtwoordloze aanmelding expliciet is toegestaan en de gebruiker minimaal één actieve Passkey heeft.

### 7.2 `roles`

- `id`
- `code UNIQUE`
- `name`
- `scope`: `system`, `organization` of `site`
- `is_system_role`

### 7.3 `permissions`

- `id`
- `code UNIQUE`
- `description`

### 7.4 `role_permissions`

Samengestelde unieke sleutel op `role_id, permission_id`.

### 7.5 `user_organization_roles`

Koppelt een gebruiker aan een rol binnen een organisatie.

Uniek op:

```text
user_id, organization_id, role_id
```

### 7.6 `user_site_roles`

Koppelt een gebruiker aan een rol binnen een specifieke Site.

### 7.7 `user_authentication_methods`

Overkoepelende registratie van beschikbare sterke authenticatiemethoden per gebruiker.

Belangrijkste kolommen:

- `id`
- `user_id`
- `method_type`: `PASSKEY`, `TOTP`, `RECOVERY_CODES`
- `status`: `PENDING`, `ACTIVE`, `REVOKED`, `LOCKED`
- `is_primary`
- `registered_at`
- `verified_at NULL`
- `last_used_at NULL`
- `revoked_at NULL`
- `revoked_by NULL`
- `revocation_reason NULL`

Uniek actief record per gebruiker en methode waar de methode slechts eenmaal mag bestaan. Passkeys kunnen meerdere records hebben via `user_passkeys`.

### 7.8 `user_passkeys`

Slaat WebAuthn/FIDO2-credentials op. De tabel bevat uitsluitend publieke credentialgegevens. Private sleutels en biometrische gegevens verlaten de authenticator niet en worden nooit door de applicatie opgeslagen.

Belangrijkste kolommen:

- `id`
- `user_id`
- `organization_id NULL`
- `authentication_method_id`
- `credential_id BYTEA NOT NULL`
- `credential_id_hash BYTEA NOT NULL`
- `public_key_cose BYTEA NOT NULL`
- `sign_count BIGINT NOT NULL DEFAULT 0`
- `aaguid UUID NULL`
- `transports TEXT[] NULL`
- `authenticator_attachment NULL`: `platform` of `cross-platform`
- `credential_type`: standaard `public-key`
- `is_discoverable`
- `backup_eligible NULL`
- `backup_state NULL`
- `user_verification_required`
- `device_name`
- `registered_at`
- `last_used_at NULL`
- `revoked_at NULL`
- `revoked_by NULL`
- `revocation_reason NULL`

Constraints en indexen:

```text
UNIQUE (credential_id_hash)
INDEX (user_id, revoked_at)
INDEX (organization_id, revoked_at)
```

`credential_id_hash` maakt veilige en efficiënte lookup mogelijk zonder het volledige credential-ID in operationele logs te gebruiken. Het originele `credential_id` blijft nodig voor protocolverwerking.

### 7.9 `user_totp_configurations`

TOTP-configuratie wordt afgescheiden van `users`, zodat activatie, rotatie en intrekking auditbaar blijven.

Belangrijkste kolommen:

- `id`
- `user_id`
- `authentication_method_id`
- `secret_encrypted BYTEA NOT NULL`
- `encryption_key_version`
- `algorithm`: standaard `SHA1`, uitbreidbaar
- `digits`: standaard `6`
- `period_seconds`: standaard `30`
- `verified_at NULL`
- `last_used_time_step BIGINT NULL`
- `last_used_at NULL`
- `revoked_at NULL`

Er is maximaal één actieve TOTP-configuratie per gebruiker.

### 7.10 `recovery_code_sets`

Registreert een uitgegeven set herstelcodes.

- `id`
- `user_id`
- `authentication_method_id`
- `generated_at`
- `generated_by`
- `expires_at NULL`
- `revoked_at NULL`
- `revoked_by NULL`
- `code_count`
- `remaining_count`

Een nieuwe set maakt alle oudere actieve sets ongeldig.

### 7.11 `recovery_codes`

Slaat uitsluitend gehashte eenmalige herstelcodes op.

- `id`
- `recovery_code_set_id`
- `code_hash BYTEA NOT NULL`
- `used_at NULL`
- `used_ip_address INET NULL`
- `revoked_at NULL`

De oorspronkelijke code wordt na uitgifte niet opnieuw opgeslagen of getoond.

### 7.12 `webauthn_challenges`

Duurzame registratie is optioneel; primaire tijdelijke opslag kan in Redis plaatsvinden. Wanneer PostgreSQL wordt gebruikt bevat de tabel:

- `id`
- `user_id NULL`
- `session_id NULL`
- `challenge_hash BYTEA NOT NULL`
- `ceremony_type`: `REGISTRATION`, `AUTHENTICATION`, `STEP_UP`
- `rp_id`
- `origin`
- `intended_action NULL`
- `created_at`
- `expires_at`
- `used_at NULL`
- `invalidated_at NULL`

De ruwe challenge wordt niet in auditlogs opgenomen. Records worden kort bewaard en periodiek verwijderd.

### 7.13 `user_sessions`

Ondersteunt actieve sessies, refresh-tokenrotatie en gerichte intrekking.

- `id`
- `user_id`
- `organization_id NULL`
- `refresh_token_hash BYTEA NOT NULL`
- `token_family_id UUID NOT NULL`
- `device_label NULL`
- `ip_address INET NULL`
- `user_agent NULL`
- `authentication_method`
- `strong_authenticated_at NULL`
- `step_up_authenticated_at NULL`
- `created_at`
- `last_seen_at`
- `expires_at`
- `revoked_at NULL`
- `revoked_by NULL`
- `revocation_reason NULL`

Alleen hashes van refresh tokens worden opgeslagen.

### 7.14 `authentication_events`

Securitylog voor aanmelding en authenticatiebeheer.

- `id`
- `user_id NULL`
- `organization_id NULL`
- `session_id NULL`
- `event_type`
- `method_type NULL`
- `result`: `SUCCESS`, `FAILURE`, `BLOCKED`
- `failure_reason NULL`
- `credential_reference_hash NULL`
- `ip_address INET NULL`
- `user_agent NULL`
- `correlation_id`
- `created_at`

Voorbeelden van `event_type`:

- `LOGIN`
- `LOGOUT`
- `PASSKEY_REGISTERED`
- `PASSKEY_REVOKED`
- `TOTP_ENABLED`
- `TOTP_REVOKED`
- `RECOVERY_CODE_USED`
- `STEP_UP`
- `SESSION_REVOKED`
- `ACCOUNT_LOCKED`

Gevoelige waarden, challenges, signatures, TOTP-geheimen en tokens worden nooit opgenomen.

### 7.15 `organization_authentication_policies`

Beleid per organisatie:

- `organization_id UNIQUE`
- `strong_authentication_required`
- `required_for_all_users`
- `allow_totp`
- `allow_passkeys`
- `allow_passwordless`
- `allow_usernameless_login`
- `require_user_verification`
- `minimum_active_methods`
- `step_up_validity_seconds`
- `session_max_age_seconds`
- `idle_timeout_seconds`
- `updated_at`
- `updated_by`

Systeembeleid kan strengere grenzen afdwingen dan organisatiebeleid.

## 8. Organisaties, Sites en installaties

### 8.1 `organizations`

- `id`
- `code UNIQUE`
- `name`
- `is_active`
- `sharepoint_marking_enabled`
- `default_timezone`

### 8.2 `sites`

- `id`
- `organization_id`
- `site_number`
- `code`
- `name`
- `storage_code UNIQUE NOT NULL`
- `storage_relative_path UNIQUE NOT NULL`
- `address_*`
- `timezone`
- `is_active`

Uniek binnen organisatie:

```text
organization_id, site_number
organization_id, code
```

`storage_code` en `storage_relative_path` zijn onveranderlijk na creatie. De zichtbare sitenaam en het functionele sitenummer maken geen deel uit van de fysieke hoofdmapnaam.

### 8.3 `installations`

Voor technische installaties, cabines, verdeelborden of andere objecten waarop documenten betrekking hebben.

- `id`
- `site_id`
- `installation_type_id`
- `code`
- `name`
- `ean_number`
- `commissioned_on`
- `decommissioned_on`
- `metadata JSONB`

### 8.4 `installation_types`

Centraal beheerde types zoals cabine, hoogspanningsinstallatie, verdeelbord of noodverlichting.

## 9. Referentiegegevens

### 9.1 `disciplines`

- `id`
- `code UNIQUE`
- `name`
- `validity_value`
- `validity_unit`: `day`, `month`, `year`
- `is_general`
- `is_active`

De vervaltermijn wordt niet in applicatiecode vastgelegd.

### 9.2 `document_types`

- `id`
- `code UNIQUE`
- `name`
- `requires_inspection_data`
- `supports_ai_analysis`
- `retention_policy_id`

### 9.3 `inspection_statuses`

Referentiewaarden:

- `UNCONFIRMED`
- `APPROVED`
- `APPROVED_WITH_REMARKS`
- `REJECTED`

De interface kan `UNCONFIRMED` tonen als `-------------`.

### 9.4 `date_source_types`

Waarden zoals:

- `EXAMINATION_DATE`
- `REPORT_DATE`
- `DOCUMENT_CONTENT`
- `FILE_METADATA`
- `MANUAL`

## 10. Documentbeheer

### 10.1 `documents`

Bevat de actuele logische documentregistratie.

- `id`
- `organization_id`
- `site_id`
- `installation_id NULL`
- `discipline_id`
- `document_type_id`
- `current_version_id NULL`
- `title`
- `document_date NULL`
- `document_date_source_id NULL`
- `ai_status`
- `validation_status`
- `sharepoint_marked`
- `sharepoint_marked_at NULL`
- `sharepoint_marked_by NULL`
- `retention_until NULL`

### 10.2 `document_versions`

Iedere fysieke upload of vervanging is een afzonderlijke versie.

- `id`
- `document_id`
- `version_number`
- `storage_path`
- `stored_filename`
- `original_filename`
- `file_hash_sha256`
- `file_size_bytes`
- `mime_type`
- `file_extension`
- `uploaded_at`
- `uploaded_by`
- `technical_metadata JSONB`
- `is_quarantined`
- `malware_scan_status`

Uniek op `document_id, version_number` en bij voorkeur op `file_hash_sha256, file_size_bytes` voor duplicaatdetectie.

### 10.3 `document_fields`

Generieke registratie van geëxtraheerde en bevestigde waarden.

- `id`
- `document_id`
- `field_code`
- `value_text NULL`
- `value_date NULL`
- `value_numeric NULL`
- `value_json NULL`
- `source_type`
- `is_confirmed`
- `confirmed_at NULL`
- `confirmed_by NULL`

Constraint: exact één waardekolom moet gevuld zijn.

### 10.4 `document_links`

Relaties tussen documenten, bijvoorbeeld opvolgend verslag, bijlage, schema of foto.

## 11. Keuringsbeheer

### 11.1 `inspection_reports`

- `id`
- `document_id UNIQUE`
- `inspection_date`
- `inspection_date_source_id`
- `report_date NULL`
- `expiry_date NULL`
- `inspection_status_id`
- `inspection_body_id NULL`
- `certificate_number NULL`
- `remarks TEXT NULL`
- `validated_at`
- `validated_by`

### 11.2 `inspection_findings`

- `id`
- `inspection_report_id`
- `finding_number NULL`
- `severity`
- `description`
- `arei_reference NULL`
- `is_resolved`
- `resolved_at NULL`
- `resolution_document_id NULL`

### 11.3 `inspection_schedules`

- `id`
- `site_id`
- `installation_id NULL`
- `discipline_id`
- `next_due_date`
- `source_report_id NULL`
- `status`
- `reminder_policy_id NULL`

Index op `next_due_date, status`.

## 12. Foto's

### 12.1 `photos`

- `id`
- `document_id UNIQUE`
- `site_id`
- `installation_id NULL`
- `photo_taken_at NULL`
- `photo_date_source_id NULL`
- `original_filename`
- `generated_filename`
- `sequence_number NULL`
- `exif_metadata JSONB`
- `requires_manual_review`

De fysieke bestandsgegevens blijven in `document_versions`.

### 12.2 `photo_batches`

Registreert batchupload, gekozen Site, standaarddiscipline, status en aantallen geslaagd/mislukt.

## 13. Risicoanalyse

### 13.1 `risk_analyses`

- `id`
- `site_id`
- `installation_id NULL`
- `document_id NULL`
- `analysis_date`
- `status`
- `version_number`
- `approved_at NULL`
- `approved_by NULL`

### 13.2 `risk_items`

- gevaar
- oorzaak
- gevolg
- waarschijnlijkheid
- impact
- risicoscore
- maatregel
- verantwoordelijke
- streefdatum
- status

## 14. AI-model-, prompt- en jobbeheer

### 14.1 `ai_models`

Logische modelregistratie met naam, type en familie.

### 14.2 `ai_model_versions`

- modelidentifier
- versie
- quantisatie
- contextlengte
- checksum
- opslaglocatie
- VRAM-profiel
- status: `test`, `production`, `retired`

### 14.3 `ai_prompts`

Logische prompt per taak en documenttype.

### 14.4 `ai_prompt_versions`

- inhoud
- outputschema JSONB
- versie
- status
- evaluatieresultaat
- geactiveerd door/op

### 14.5 `ai_jobs`

- `id`
- `document_version_id`
- `job_type`
- `model_version_id`
- `prompt_version_id NULL`
- `status`
- `priority`
- `queued_at`
- `started_at NULL`
- `finished_at NULL`
- `retry_count`
- `worker_name NULL`
- `gpu_identifier NULL`
- `raw_response JSONB NULL`
- `validated_response JSONB NULL`
- `error_code NULL`
- `error_message NULL`
- `duration_ms NULL`

Indexen op `status, priority, queued_at` en `document_version_id`.

### 14.6 `ai_field_predictions`

Per veld:

- voorgestelde waarde
- confidence
- bronpagina of tekstfragment
- bounding box indien beschikbaar
- gekozen kenniscontext

### 14.7 `ai_feedback`

- `ai_field_prediction_id`
- `proposed_value JSONB`
- `confirmed_value JSONB`
- `was_correct`
- `correction_reason NULL`
- `corrected_at`
- `corrected_by`

## 15. Kennisbank en RAG

### 15.1 `knowledge_entities`

Generieke entiteiten zoals Site, cabine, installatie, keuringsinstantie, AREI-artikel of technisch begrip.

- `entity_type`
- `canonical_name`
- `external_reference NULL`
- `status`
- `metadata JSONB`

### 15.2 `knowledge_aliases`

Alternatieve schrijfwijzen en codes.

Uniek op `normalized_alias, entity_type` waar dit inhoudelijk mogelijk is.

### 15.3 `knowledge_relations`

- `source_entity_id`
- `relation_type`
- `target_entity_id`
- `confidence`
- `approval_status`
- `valid_from NULL`
- `valid_until NULL`
- `source_document_id NULL`
- `approved_by NULL`
- `approved_at NULL`

### 15.4 `knowledge_rules`

Beheerde herkenningsregels met patroon, doelfield, doelwaarde, prioriteit, geldigheid en goedkeuringsstatus.

### 15.5 `knowledge_chunks`

Documentfragmenten voor RAG:

- `document_version_id`
- `chunk_index`
- `page_number NULL`
- `content`
- `content_hash`
- `token_count`
- `metadata JSONB`
- `embedding vector(...) NULL`
- `embedding_model_version_id NULL`

Indexstrategie voor vectoren wordt gekozen op basis van omvang en pgvector-versie.

### 15.6 `rag_queries`

Auditbare registratie van kennisvragen zonder onbeperkt gevoelige promptinhoud te bewaren.

- gebruiker
- querytype
- geselecteerde bronnen
- modelversie
- antwoordstatus
- duur

## 16. Meldingen en e-mail

### 16.1 `notifications`

In-appmeldingen per gebruiker, type, status en gerelateerd object.

### 16.2 `email_queue`

- ontvanger
- template
- payload
- geplande verzendtijd
- status
- retries
- foutmelding

### 16.3 `reminder_policies`

Configureerbare termijnen voor waarschuwingen vóór vervaldatums.

## 17. Instellingen

### 17.1 `settings`

Instellingen krijgen een scope:

- system
- organization
- site
- user

Kolommen:

- `key`
- `value JSONB`
- `value_type`
- `scope_type`
- `scope_id NULL`
- `is_secret`

Geheimen worden bij voorkeur buiten de database in een secretsysteem bewaard; indien noodzakelijk alleen versleuteld.

## 18. Audit en logging

### 18.1 `audit_log`

Onveranderbare bedrijfsaudit:

- actor
- actie
- objecttype en object-id
- organisatie en Site
- oude en nieuwe waarden JSONB
- timestamp
- correlation-id
- IP-adres en user-agent waar toegestaan

Geen wachtwoorden, TOTP-geheimen, WebAuthn-challenges, signatures, private sleutels, herstelcodes, tokens of volledige documentinhoud.

### 18.2 `system_log`

Voor applicatie- en integratiefouten met retentiebeleid. Operationele logs kunnen op termijn naar een centrale loggingstack worden verplaatst.

## 19. Indexstrategie

Minimaal:

- Alle foreign keys krijgen een index
- Partiële indexen op actieve, niet-verwijderde objecten
- B-tree op datums, statusvelden en codes
- GIN op relevante JSONB-kolommen
- GIN/GiST trigramindex op zoekvelden zoals Site- en documentnamen
- Full-textindex op bevestigde documenttekst
- Vectorindex alleen wanneer het aantal embeddings dit rechtvaardigt
- Unieke index op gehashte WebAuthn credential-ID's
- Partiële index op actieve Passkeys per gebruiker
- Index op actieve sessies en vervaldatum
- Index op mislukte authenticatie-events per gebruiker en tijdstip

Voorbeelden:

```sql
CREATE INDEX ix_inspection_schedules_due
ON inspection_schedules (next_due_date)
WHERE status = 'OPEN';

CREATE UNIQUE INDEX uq_user_passkeys_credential_hash
ON user_passkeys (credential_id_hash);

CREATE INDEX ix_user_passkeys_active
ON user_passkeys (user_id, last_used_at)
WHERE revoked_at IS NULL;

CREATE INDEX ix_user_sessions_active
ON user_sessions (user_id, expires_at)
WHERE revoked_at IS NULL;
```

## 20. Constraints en gegevenskwaliteit

- `expiry_date >= inspection_date`
- Bestandsgrootte groter dan nul en maximaal volgens applicatiebeleid
- Keuringsstatus mag bij definitieve validatie niet `UNCONFIRMED` zijn
- Eén actuele documentversie per document
- Geen overlappende actieve unieke codes binnen dezelfde scope
- Kennisrelaties mogen niet naar zichzelf verwijzen tenzij expliciet toegestaan
- AI-output wordt nooit rechtstreeks definitief zonder validatiestatus
- Een actieve Passkey moet een credential-ID en publieke sleutel bevatten
- Een ingetrokken Passkey kan niet opnieuw worden gebruikt
- Een herstelcode kan maximaal eenmaal worden gebruikt
- Een WebAuthn-challenge kan maximaal eenmaal worden gebruikt en niet na vervaldatum
- Het verwijderen van de laatste actieve sterke authenticatiemethode wordt in de servicelaag geblokkeerd
- Wachtwoordloze gebruikers moeten minimaal één actieve Passkey hebben
- `storage_code` en `storage_relative_path` van een Site mogen na creatie niet worden gewijzigd

Complexe domeinregels blijven in de servicelaag, aangevuld met databaseconstraints waar betrouwbaar afdwingbaar.

## 21. Historiek en soft delete

- Documentversies en AI-jobresultaten worden niet overschreven
- Kritieke wijzigingen worden via auditlog vastgelegd
- Soft-deleted objecten worden standaard uitgesloten
- Referentiewaarden die in gebruik zijn worden gedeactiveerd, niet verwijderd
- Herstel van verwijderde gegevens vereist een bevoegde rol en auditregistratie
- Ingetrokken Passkeys, TOTP-configuraties en sessies worden historisch bewaard volgens het beveiligingsretentiebeleid
- Gebruikte herstelcodes worden niet opnieuw geactiveerd

## 22. Migratiestrategie

- Alembic als enige mechanisme voor schemawijzigingen
- Iedere migratie bevat upgrade en waar haalbaar downgrade
- Voor destructieve migraties eerst back-up en datamigratieplan
- Grote indexen in productie waar mogelijk concurrent aanmaken
- Migraties eerst testen op een representatieve kopie
- Applicatieversie en databaseschemaversie worden samen geregistreerd
- Bestaande TOTP-kolommen in `users` worden gecontroleerd gemigreerd naar `user_totp_configurations`
- Bestaande herstelcodes worden opnieuw uitgegeven wanneer het oude hashformaat onvoldoende sterk of niet compatibel is

## 23. Back-up en herstel

- Dagelijkse PostgreSQL-back-up naar Synology NAS
- Extra back-up vóór release of migratie
- Point-in-time recovery als latere uitbreiding
- Periodieke restoretest
- Apart beleid voor database, documentopslag en AI-artifacts
- Back-up van embeddings kan opnieuw opbouwbaar zijn, maar kennisregels en feedback zijn bedrijfskritiek
- Authenticatiegegevens vallen onder versleutelde databaseback-ups en streng toegangsbeheer
- Encryptiesleutels voor TOTP-geheimen worden niet samen met de databaseback-up opgeslagen

## 24. Initiële implementatievolgorde

1. Gebruikers, rollen en autorisatie
2. TOTP, herstelcodes en authenticatiebeleid
3. WebAuthn/Passkeys, challenges en sessiebeheer
4. Organisaties, Sites en referentiegegevens
5. Documenten en versies
6. Keuringsrapporten en planning
7. Foto- en batchregistratie
8. AI-modellen, prompts, jobs en feedback
9. Kennisregels
10. Documentchunks en pgvector
11. Rapportering, notificaties en verdere modules

## 25. Openstaande keuzes

- Exacte dimensie van embeddingvectoren
- pgvector versus afzonderlijke vectordatabase op grotere schaal
- Volledige bewaartermijnen per documenttype
- Point-in-time recovery
- Centrale secretsopslag
- Partitionering van audit-, job-, authenticatie- en embeddingtabellen
- Definitieve taxonomie van kennisentiteiten en relaties
- Definitieve retentie van challenges, sessies en authentication events
- Definitief attestationbeleid en eventuele allowlist van AAGUID's
- Sleutelbeheer en rotatiestrategie voor versleutelde TOTP-geheimen