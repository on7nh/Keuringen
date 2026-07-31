# API Ontwerp

## Digitaal Keurings- en Documentbeheer

**Versie:** 1.1 Concept  
**Status:** Uitgewerkt technisch ontwerp

## 1. Doel

Dit document beschrijft de interne REST API van het platform. De API vormt de scheiding tussen frontend, backend, AI-platform, opslag, rapportering en toekomstige integraties.

## 2. Architectuurprincipes

- REST over HTTPS
- JSON als standaardformaat
- OpenAPI 3.1 als contract
- API-first ontwikkeling
- Versiebeheer via `/api/v1`
- UUID's als publieke identifiers
- UTC-tijdstippen in ISO 8601
- Idempotentie voor uploads en kritieke writes
- Geen directe frontendtoegang tot database, NAS of AI-modelservers
- Autorisatie op systeem-, organisatie- en Site-niveau
- Correlation ID in iedere request en response
- Sterke authenticatie via TOTP en WebAuthn/Passkeys
- WebAuthn-challenges zijn kort geldig, eenmalig bruikbaar en aan sessie en actie gekoppeld
- Biometrische gegevens worden nooit door de API ontvangen of opgeslagen

## 3. Basisstructuur

```text
/api/v1/auth
/api/v1/users
/api/v1/organizations
/api/v1/sites
/api/v1/installations
/api/v1/disciplines
/api/v1/document-types
/api/v1/documents
/api/v1/uploads
/api/v1/photo-batches
/api/v1/inspections
/api/v1/risk-analyses
/api/v1/ai
/api/v1/knowledge
/api/v1/search
/api/v1/reports
/api/v1/notifications
/api/v1/settings
/api/v1/audit
```

## 4. Authenticatie en sessies

### 4.1 Authenticatiemethoden

De API ondersteunt:

- wachtwoord plus TOTP;
- wachtwoord plus Passkey;
- wachtwoordloze Passkey-login, wanneer door beleid toegestaan;
- usernameless Passkey-login met discoverable credentials;
- herstelcodes als gecontroleerde noodprocedure;
- step-up authenticatie voor gevoelige acties.

SMS en e-mail-OTP worden niet ondersteund als sterke authenticatiemethode.

### 4.2 Initiële login met wachtwoord

`POST /api/v1/auth/login`

Request:

```json
{
  "email": "user@example.org",
  "password": "********"
}
```

Mogelijke response:

```json
{
  "status": "STRONG_AUTH_REQUIRED",
  "challenge_id": "uuid",
  "allowed_methods": ["PASSKEY", "TOTP", "RECOVERY_CODE"],
  "expires_at": "2026-07-30T20:00:00Z"
}
```

Wanneer geen aanvullende verificatie nodig is, retourneert de API direct een sessie of tokens.

### 4.3 TOTP-verificatie

`POST /api/v1/auth/totp/verify`

Request:

```json
{
  "challenge_id": "uuid",
  "code": "123456"
}
```

De code mag binnen hetzelfde tijdsvenster niet opnieuw worden gebruikt.

### 4.4 Passkey-registratie

#### Registratieopties

`POST /api/v1/auth/passkey/register/options`

Vereist een aangemelde sessie en recente step-up authenticatie.

Request:

```json
{
  "device_name": "Laptop kantoor",
  "authenticator_attachment": "platform"
}
```

Response bevat WebAuthn `PublicKeyCredentialCreationOptions`, waaronder:

- challenge;
- RP-gegevens;
- user-handle;
- ondersteunde algoritmen;
- authenticator selection;
- exclude credentials;
- timeout;
- attestationbeleid.

#### Registratie verifiëren

`POST /api/v1/auth/passkey/register/verify`

Request:

```json
{
  "challenge_id": "uuid",
  "device_name": "Laptop kantoor",
  "credential": {
    "id": "base64url",
    "rawId": "base64url",
    "type": "public-key",
    "response": {
      "clientDataJSON": "base64url",
      "attestationObject": "base64url",
      "transports": ["internal"]
    }
  }
}
```

De backend valideert minimaal challenge, origin, RP ID hash, client data type, attestation, user presence en user verification volgens beleid.

### 4.5 Passkey-login

#### Loginopties

`POST /api/v1/auth/passkey/login/options`

Request met gekende gebruiker:

```json
{
  "email": "user@example.org"
}
```

Voor usernameless login kan de request leeg zijn wanneer dit is toegestaan.

Response bevat WebAuthn `PublicKeyCredentialRequestOptions` met challenge, RP ID, timeout, toegestane credentials indien van toepassing en vereiste user verification.

#### Login verifiëren

`POST /api/v1/auth/passkey/login/verify`

Request:

```json
{
  "challenge_id": "uuid",
  "credential": {
    "id": "base64url",
    "rawId": "base64url",
    "type": "public-key",
    "response": {
      "clientDataJSON": "base64url",
      "authenticatorData": "base64url",
      "signature": "base64url",
      "userHandle": "base64url"
    }
  }
}
```

De backend valideert minimaal:

- challenge en vervaldatum;
- eenmalig gebruik;
- origin en RP ID hash;
- credentialstatus;
- cryptografische signature;
- user presence;
- user verification;
- sign counter, indien bruikbaar.

Na succesvolle verificatie wordt een sessie of tokenpaar uitgegeven.

### 4.6 Passkeybeheer

- `GET /api/v1/auth/passkey/list`
- `PATCH /api/v1/auth/passkey/{passkey_id}`
- `DELETE /api/v1/auth/passkey/{passkey_id}`

Voorbeeld wijziging apparaatnaam:

```json
{
  "device_name": "iPhone werk"
}
```

Verwijderen vereist recente step-up authenticatie. De API blokkeert het verwijderen van de laatste bruikbare authenticatiemethode zonder vervangende methode of administratieve herstelprocedure.

### 4.7 TOTP-beheer

- `POST /api/v1/auth/totp/setup`
- `POST /api/v1/auth/totp/confirm`
- `DELETE /api/v1/auth/totp`

`setup` retourneert een tijdelijke registratie-ID, QR-codegegevens en een handmatige sleutel. Het TOTP-geheim wordt nooit na bevestiging opnieuw geretourneerd.

### 4.8 Herstelcodes

- `POST /api/v1/auth/recovery-codes/generate`
- `GET /api/v1/auth/recovery-codes/status`
- `POST /api/v1/auth/recovery-code/use`

Genereren vereist recente step-up authenticatie. Een nieuwe set maakt alle vorige sets ongeldig. Codes worden slechts eenmaal getoond en uitsluitend gehasht opgeslagen.

### 4.9 Step-up authenticatie

#### Step-up starten

`POST /api/v1/auth/step-up/options`

Request:

```json
{
  "intended_action": "SITE_MIGRATION_START",
  "resource_id": "uuid"
}
```

Response:

```json
{
  "step_up_id": "uuid",
  "allowed_methods": ["PASSKEY", "TOTP"],
  "expires_at": "2026-07-30T20:00:00Z"
}
```

Voor Passkey kan dezelfde response direct WebAuthn request options bevatten.

#### Step-up verifiëren

- `POST /api/v1/auth/step-up/passkey/verify`
- `POST /api/v1/auth/step-up/totp/verify`

Na succesvolle verificatie wordt de sessie gedurende een korte configureerbare periode als step-up geverifieerd. De bevestiging is aan de gebruiker, sessie en eventueel de bedoelde actie gekoppeld.

Gevoelige endpoints kunnen bij ontbrekende recente verificatie antwoorden met:

```json
{
  "error": {
    "code": "STEP_UP_REQUIRED",
    "message": "Voor deze actie is aanvullende verificatie vereist.",
    "details": {
      "intended_action": "SITE_MIGRATION_START",
      "allowed_methods": ["PASSKEY", "TOTP"]
    },
    "correlation_id": "uuid"
  }
}
```

### 4.10 Sessies en tokens

- korte access token;
- refresh token rotatie;
- alleen een hash van refresh tokens in opslag;
- intrekken bij logout, beveiligingsincident of credentialwijziging;
- geen tokens in queryparameters;
- sessies zijn per apparaat raadpleegbaar en intrekbaar.

Endpoints:

- `POST /api/v1/auth/refresh`
- `POST /api/v1/auth/logout`
- `POST /api/v1/auth/logout-all`
- `GET /api/v1/auth/sessions`
- `DELETE /api/v1/auth/sessions/{session_id}`
- `GET /api/v1/auth/me`
- `POST /api/v1/auth/password/change`

### 4.11 Samenvatting authenticatie-endpoints

- `POST /auth/login`
- `POST /auth/totp/verify`
- `POST /auth/totp/setup`
- `POST /auth/totp/confirm`
- `DELETE /auth/totp`
- `POST /auth/passkey/register/options`
- `POST /auth/passkey/register/verify`
- `POST /auth/passkey/login/options`
- `POST /auth/passkey/login/verify`
- `GET /auth/passkey/list`
- `PATCH /auth/passkey/{passkey_id}`
- `DELETE /auth/passkey/{passkey_id}`
- `POST /auth/recovery-codes/generate`
- `GET /auth/recovery-codes/status`
- `POST /auth/recovery-code/use`
- `POST /auth/step-up/options`
- `POST /auth/step-up/passkey/verify`
- `POST /auth/step-up/totp/verify`
- `POST /auth/refresh`
- `POST /auth/logout`
- `POST /auth/logout-all`
- `GET /auth/sessions`
- `DELETE /auth/sessions/{session_id}`
- `POST /auth/password/change`
- `GET /auth/me`

## 5. Autorisatie

Iedere request wordt gevalideerd op:

1. Geldige identiteit
2. Actieve gebruiker
3. Geldige sessie
4. Vereist niveau van sterke authenticatie
5. Recente step-up verificatie indien van toepassing
6. Organisatiebereik
7. Sitebereik
8. Vereiste permissie
9. Status van het object

Voorbeeldpermissies:

- `documents.read`
- `documents.upload`
- `documents.validate`
- `inspections.manage`
- `risk_analyses.manage`
- `ai.feedback.manage`
- `knowledge.approve`
- `settings.manage`
- `audit.read`
- `authentication.policy.manage`
- `authentication.credentials.manage`
- `sessions.manage`

## 6. Algemene requestconventies

### 6.1 Headers

```text
Authorization: Bearer <token>
Content-Type: application/json
X-Correlation-ID: <uuid>
Idempotency-Key: <uuid>   # bij ondersteunde writes
```

Voor cookiegebaseerde sessies is daarnaast CSRF-bescherming verplicht.

### 6.2 Paginering

```text
?page=1&page_size=50
```

Response:

```json
{
  "items": [],
  "page": 1,
  "page_size": 50,
  "total": 0,
  "total_pages": 0
}
```

### 6.3 Sortering en filtering

```text
?sort=-created_at,title
?site_id=<uuid>
?status=APPROVED
?created_from=2026-01-01
```

Alle filters worden expliciet per endpoint gedefinieerd.

## 7. Foutmodel

Standaardresponse:

```json
{
  "error": {
    "code": "DOCUMENT_VALIDATION_FAILED",
    "message": "Het document kan nog niet definitief worden opgeslagen.",
    "details": [],
    "correlation_id": "uuid"
  }
}
```

Authenticatiefouten gebruiken generieke meldingen om accountenumeratie te beperken.

Belangrijke foutcodes:

- `AUTHENTICATION_FAILED`
- `STRONG_AUTH_REQUIRED`
- `STEP_UP_REQUIRED`
- `WEBAUTHN_CHALLENGE_EXPIRED`
- `WEBAUTHN_CHALLENGE_USED`
- `WEBAUTHN_ORIGIN_INVALID`
- `WEBAUTHN_RP_ID_INVALID`
- `WEBAUTHN_SIGNATURE_INVALID`
- `PASSKEY_REVOKED`
- `LAST_AUTHENTICATION_METHOD`
- `TOTP_INVALID`
- `RECOVERY_CODE_INVALID`
- `SESSION_REVOKED`
- `ACCOUNT_LOCKED`

Belangrijke HTTP-statussen:

- `200` geslaagd
- `201` aangemaakt
- `202` asynchrone verwerking aanvaard
- `204` geslaagd zonder body
- `400` ongeldige request
- `401` niet aangemeld of authenticatie mislukt
- `403` onvoldoende rechten of onvoldoende authenticatieniveau
- `404` niet gevonden binnen toegestane scope
- `409` conflict
- `413` bestand te groot
- `415` ongeldig bestandstype
- `422` inhoudelijk niet valide
- `429` limiet overschreden
- `500` interne fout
- `503` afhankelijke service niet beschikbaar

## 8. Organisaties, Sites en installaties

### Organisaties

- `GET /organizations`
- `POST /organizations`
- `GET /organizations/{id}`
- `PATCH /organizations/{id}`
- `DELETE /organizations/{id}`
- `GET /organizations/{id}/authentication-policy`
- `PATCH /organizations/{id}/authentication-policy`

Het wijzigen van authenticatiebeleid vereist step-up authenticatie en de permissie `authentication.policy.manage`.

### Sites

- `GET /sites`
- `POST /sites`
- `GET /sites/{id}`
- `PATCH /sites/{id}`
- `DELETE /sites/{id}`
- `GET /sites/{id}/summary`
- `GET /sites/{id}/documents`
- `GET /sites/{id}/inspections`

### Installaties

- `GET /installations`
- `POST /installations`
- `GET /installations/{id}`
- `PATCH /installations/{id}`
- `DELETE /installations/{id}`

## 9. Document API

- `GET /documents`
- `GET /documents/{id}`
- `PATCH /documents/{id}`
- `POST /documents/{id}/validate`

Documentfilters omvatten organisatie, Site, installatie, discipline, documenttype, datum, keuringsstatus, vervaldatum, AI-status, validatiestatus en SharePoint-markering.

Optimistic locking gebruikt `row_version`; conflicten retourneren `409 ROW_VERSION_CONFLICT`.

## 10. Upload API

- `POST /uploads`
- `PUT /uploads/{upload_id}/content`
- `POST /uploads/{upload_id}/complete`
- `GET /uploads/{upload_id}`

Uploads zijn maximaal 100 MB en ondersteunen PDF, JPG/JPEG, DWG en XLSX. Verwerking gebeurt streaming, met hashcontrole en tijdelijke quarantaine.

## 11. Foto-batch API

- `POST /photo-batches`
- `POST /photo-batches/{id}/files`
- `POST /photo-batches/{id}/complete`
- `GET /photo-batches/{id}`
- `GET /photo-batches/{id}/items`
- `PATCH /photo-batches/{id}/items/{item_id}`
- `POST /photo-batches/{id}/confirm`

De API retourneert per foto de oorspronkelijke bestandsnaam, voorgestelde nieuwe naam, gevonden datum en bron, conflictstatus en noodzaak tot manuele controle.

## 12. Keurings-API

- `GET /inspections`
- `GET /inspections/{id}`
- `PATCH /inspections/{id}`
- `GET /inspections/due`
- `GET /inspections/calendar`
- `POST /inspections/{id}/findings`
- `PATCH /inspections/{id}/findings/{finding_id}`

`GET /inspections/due` ondersteunt tijdvensters zoals 30, 60, 90 en 180 dagen.

## 13. AI Job API

- `POST /ai/jobs`
- `GET /ai/jobs/{id}`
- `GET /ai/jobs/{id}/result`
- `POST /ai/jobs/{id}/retry`

Alle AI-jobs zijn asynchroon en idempotent per documentversie, jobtype, model- en promptversie.

## 14. AI-validatie en feedback

- `GET /documents/{id}/ai-proposals`
- `POST /documents/{id}/ai-proposals/{proposal_id}/confirm`
- `POST /documents/{id}/ai-proposals/{proposal_id}/correct`
- `GET /ai/feedback`
- `GET /ai/quality/summary`
- `GET /ai/quality/by-field`
- `GET /ai/quality/by-model`

## 15. Knowledge API

- `GET /knowledge/entities`
- `POST /knowledge/entities`
- `GET /knowledge/entities/{id}`
- `PATCH /knowledge/entities/{id}`
- `GET /knowledge/relations`
- `POST /knowledge/relations`
- `POST /knowledge/relations/{id}/approve`
- `POST /knowledge/relations/{id}/reject`
- `GET /knowledge/rules`
- `POST /knowledge/rules`
- `POST /knowledge/rules/{id}/test`
- `POST /knowledge/rules/{id}/activate`

## 16. Zoek- en vraag-API

### 16.1 Hybride zoeken

`POST /search`

### 16.2 Kennisvraag

`POST /knowledge/query`

Response bevat altijd antwoord, gebruikte bronnen, document-ID's, paginanummers of fragmenten, modelversie en een waarschuwing wanneer de bronbasis onvoldoende is.

## 17. Rapportering

- `GET /reports/inspection-expiry`
- `GET /reports/document-completeness`
- `GET /reports/ai-quality`
- `GET /reports/findings`
- `POST /reports/export`
- `GET /reports/exports/{id}`

Exports zijn asynchroon wanneer de dataset groot is. Gevoelige of omvangrijke exports kunnen step-up authenticatie vereisen.

## 18. Realtime gebeurtenissen

Voor voortgang en meldingen wordt Server-Sent Events aanbevolen:

`GET /events`

Eventtypes:

- `upload.progress`
- `document.processing.completed`
- `document.validation.required`
- `ai.job.progress`
- `ai.job.completed`
- `report.ready`
- `notification.created`
- `security.session.revoked`
- `security.credential.changed`

WebSockets blijven mogelijk voor toekomstige interactieve AI-functies.

## 19. Rate limiting

Voorbeelden:

- login: streng per IP en account;
- WebAuthn options: per IP, account en sessie;
- WebAuthn verify: streng per challenge en account;
- TOTP verify: streng per account en challenge;
- recovery codes: zeer streng per account;
- step-up: per sessie en actie;
- search: per gebruiker;
- knowledge query: per gebruiker en modelcapaciteit;
- upload: per organisatie en gelijktijdige sessies;
- AI retry: beperkt om jobstormen te voorkomen.

Limieten zijn configureerbaar. Herhaalde mislukte verificaties kunnen tijdelijke blokkering en securitylogging veroorzaken.

## 20. Beveiliging

- Alleen HTTPS
- CORS alleen voor goedgekeurde origins
- Exacte origin- en RP ID-validatie voor WebAuthn
- CSRF-bescherming wanneer cookies worden gebruikt
- Invoervalidatie volgens JSON Schema
- MIME- en bestandsinhoudcontrole
- Geen ruwe stacktraces naar clients
- Object-level authorization op ieder endpoint
- Downloadlinks tijdelijk en geautoriseerd
- Audit voor exports, downloads, validaties, authenticatie- en beheeracties
- Challenges, TOTP-geheimen, signatures, private sleutels, herstelcodes en tokens worden nooit gelogd
- Credential-ID's worden in logs uitsluitend gehasht of gepseudonimiseerd opgenomen wanneer noodzakelijk
- WebAuthn verification endpoints accepteren uitsluitend base64url volgens het contractschema
- Challenges worden na gebruik atomair ongeldig gemaakt

## 21. Interne AI API

De backend communiceert met het lokale AI-platform via een afzonderlijke interne API:

```text
POST /internal/v1/ocr/jobs
POST /internal/v1/vision/jobs
POST /internal/v1/inference/jobs
POST /internal/v1/embeddings/jobs
GET  /internal/v1/jobs/{id}
GET  /internal/v1/models
GET  /internal/v1/health
```

Deze API is niet bereikbaar vanuit het gebruikersnetwerk.

## 22. OpenAPI en clientgeneratie

- De OpenAPI-specificatie is onderdeel van de repository
- WebAuthn request- en response-objecten krijgen expliciete base64url-schema's
- Contractwijzigingen worden gereviewd
- Frontendtypes worden automatisch gegenereerd
- Breaking changes vereisen een nieuwe major API-versie
- CI valideert voorbeelden en schema's

## 23. Teststrategie

- Unit tests voor validatie en autorisatie
- Contracttests tegen OpenAPI
- Integratietests met PostgreSQL, Redis en opslag
- Securitytests voor objecttoegang
- WebAuthn-tests voor registratie, login, usernameless login en step-up
- Negatieve tests voor verkeerde origin, RP ID, challenge, signature en ingetrokken credential
- Replaytests voor gebruikte challenges en TOTP-codes
- Tests voor sign-countergedrag en authenticators zonder bruikbare counter
- Tests voor verwijderen van de laatste authenticatiemethode
- Sessierotatie- en sessie-intrekkingstests
- Uploadtests voor formaat, grootte en beschadigde bestanden
- AI-foutscenario's en timeouts
- Belastbaarheidstests op zoeken, uploads, authenticatie-endpoints en jobwachtrij

## 24. Openstaande keuzes

- JWT in header versus beveiligde sessiecookies
- Definitieve RP ID en toegestane origins per omgeving
- Attestationbeleid en eventuele AAGUID-allowlist
- Exact beleid voor usernameless login
- Geldigheidsduur van challenges en step-up verificatie
- SSE versus WebSocket voor alle realtime functies
- Chunked upload voor bestanden tot 100 MB
- API gateway-product
- Externe integratie-API en authenticatiemethode
- Exacte exportformaten en maximale rapportgroottes