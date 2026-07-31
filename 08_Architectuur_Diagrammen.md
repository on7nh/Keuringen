# Architectuurdiagrammen

## Digitaal Keurings- en Documentbeheer

**Versie:** 1.2 Concept  
**Status:** Architectuurvoorstel

## 1. Doel van dit document

Dit document visualiseert de samenhang tussen frontend, backend, database, opslag, AI-platform, documentverwerking, naamgeving, migratie, sterke authenticatie, monitoring en herstel.

De diagrammen zijn opgesteld in Mermaid-formaat en gelden samen met de andere ontwerpdocumenten als richtinggevend architectuurcontract.

## 2. Systeemcontext

```mermaid
flowchart LR
    User[Medewerker / Keurder]
    Admin[Validator / Beheerder]
    Browser[Webbrowser]
    Platform[Digitaal Keurings- en Documentbeheer]
    Authenticator[Platformauthenticator / Security key]
    AuthApp[Authenticator-app]
    Mail[Mailbox keuringen@elecon.be]
    SMTP[SMTP-server]
    NAS[Synology NAS]
    AI[On-prem AI-platform]
    SharePoint[SharePoint - handmatige status]

    User --> Browser
    Admin --> Browser
    Browser --> Platform
    Browser <--> Authenticator
    AuthApp --> User
    Mail --> Platform
    Platform --> SMTP
    Platform --> NAS
    Platform --> AI
    Platform -. geen automatische synchronisatie .-> SharePoint
```

Belangrijkste regels:

- Gebruikers werken via HTTPS.
- Sterke authenticatie ondersteunt TOTP en WebAuthn/Passkeys.
- Biometrische verificatie gebeurt lokaal op het apparaat; de applicatie bewaart geen biometrische gegevens.
- PostgreSQL is de bron van waarheid voor metadata, relaties, credentials en audit.
- Documentbestanden staan op de Synology NAS.
- AI-verwerking gebeurt op het gedeelde on-prem AI-platform.

## 3. Containerarchitectuur

```mermaid
flowchart TB
    subgraph Client[Clientlaag]
        Browser[React / TypeScript Webfrontend]
        WebAuthn[Browser WebAuthn API]
        Microphone[Microfoon]
    end

    subgraph Application[Applicatielaag]
        Proxy[Reverse Proxy / TLS]
        API[FastAPI Backend]
        Auth[Authenticatie- en sessieservice]
        Authorization[Autorisatieservice]
        Naming[Centrale Naamgevingsservice]
        Worker[Worker Services]
        Scheduler[Scheduler]
        Realtime[SSE Event Service]
    end

    subgraph Data[Datalaag]
        DB[(PostgreSQL)]
        Redis[(Redis / Queue / Challenges)]
        NAS[(Synology NAS)]
    end

    subgraph AIPlatform[On-prem AI-platform]
        Gateway[AI Gateway]
        OCR[OCR]
        Vision[Vision]
        LLM[LLM]
        STT[Speech-to-Text]
        Embeddings[Embeddings]
        RAG[Knowledge / RAG]
    end

    Browser --> Proxy --> API
    Browser --> WebAuthn
    Microphone --> Browser
    API --> Auth
    API --> Authorization
    Auth --> DB
    Auth --> Redis
    API --> DB
    API --> Redis
    API --> Naming
    API --> NAS
    API --> Realtime
    Scheduler --> Redis
    Redis --> Worker
    Worker --> DB
    Worker --> NAS
    Worker --> Naming
    API --> Gateway
    Worker --> Gateway
    Gateway --> OCR
    Gateway --> Vision
    Gateway --> LLM
    Gateway --> STT
    Gateway --> Embeddings
    Gateway --> RAG
    Realtime --> Browser
```

## 4. Deploymentarchitectuur

```mermaid
flowchart TB
    Users[Intern netwerk / VPN]

    subgraph Proxmox[Proxmox]
        subgraph WebVM[Debian 12 - Webapplicatie]
            Proxy[Reverse Proxy]
            Frontend[Frontend Container]
            Backend[Backend Container]
            Workers[Worker Containers]
            Scheduler[Scheduler Container]
            Redis[Redis Container]
        end
        subgraph DBVM[Debian 12 - Database]
            PostgreSQL[(PostgreSQL)]
        end
    end

    subgraph AIHost[HPE ProLiant ML350]
        AIGateway[AI Gateway]
        AIServices[OCR / Vision / LLM / STT / RAG]
        GPUs[3 x RTX 3090]
    end

    subgraph Synology[Synology NAS]
        Files[(Documentopslag)]
        Backups[(PostgreSQL-back-ups)]
    end

    Users -->|HTTPS 443| Proxy
    Proxy --> Frontend
    Proxy --> Backend
    Backend --> PostgreSQL
    Backend --> Redis
    Workers --> Redis
    Workers --> PostgreSQL
    Backend --> Files
    Workers --> Files
    Backend --> AIGateway
    Workers --> AIGateway
    AIGateway --> AIServices --> GPUs
    PostgreSQL --> Backups
```

## 5. Documentupload en verwerking

```mermaid
sequenceDiagram
    actor U as Gebruiker
    participant UI as Webfrontend
    participant API as Backend
    participant Q as Redis / Queue
    participant W as Worker
    participant AI as AI-platform
    participant N as Naamgevingsservice
    participant DB as PostgreSQL
    participant NAS as Synology NAS

    U->>UI: Selecteer bestanden
    UI->>API: Upload naar quarantaine
    API->>API: Valideer MIME, grootte en hash
    API->>DB: Registreer upload
    API->>Q: Maak job aan
    API-->>UI: Upload aanvaard

    loop Eén bestand per stap
        Q->>W: Volgend bestand
        W->>AI: OCR / Vision / extractie
        AI-->>W: Voorstel + confidence
        W->>N: Genereer definitieve naam
        N->>DB: Controleer en reserveer naam
        N-->>W: Geldige naam
        W->>NAS: Sla bestand op
        W->>W: Verifieer hash
        W->>DB: Werk metadata en audit bij
        W-->>UI: SSE voortgang
    end
```

De definitieve naamgeneratie en bestandsmutatie gebeuren altijd sequentieel.

## 6. Centrale bestandsnaamgeneratie

```mermaid
flowchart TD
    Start[Metadata beschikbaar]
    Read[Lees actuele metadata]
    Compose[Stel naam samen]
    Validate[Valideer conventie]
    Exists{Naam of pad bestaat?}
    Classify{Duplicaat, versie of nieuw?}
    Duplicate[Sla duplicaat over]
    Version[Koppel als nieuwe versie]
    Counter[Voeg _01, _02, ... toe]
    Reserve[Reserveer naam]
    Store[Sla één bestand op]
    Verify[Controleer doelpad en hash]
    Commit[Werk database en audit bij]

    Start --> Read --> Compose --> Validate --> Exists
    Exists -- Nee --> Reserve
    Exists -- Ja --> Classify
    Classify -- Duplicaat --> Duplicate
    Classify -- Versie --> Version
    Classify -- Nieuw --> Counter --> Validate
    Reserve --> Store --> Verify --> Commit
```

## 7. Onveranderlijke fysieke opslag

```mermaid
flowchart LR
    SiteID[Onveranderlijke site_id]
    StorageCode[Onveranderlijke storage_code]
    Folder[Fysieke map SITE_00001247]
    Name[Zichtbare sitenaam Putte]
    Number[TMP001 of 185]
    Filename[Zichtbare bestandsnaam]

    SiteID --> StorageCode --> Folder
    SiteID --> Name
    SiteID --> Number
    Name --> Filename
    Number --> Filename
```

De fysieke hoofdmap wordt nooit hernoemd wanneer de zichtbare sitenaam of het sitenummer wijzigt.

## 8. Tijdelijke Site naar definitieve Site

```mermaid
sequenceDiagram
    actor A as Bevoegde gebruiker
    participant UI as Migratiewizard
    participant API as Backend
    participant Auth as Authenticatieservice
    participant N as Naamgevingsservice
    participant DB as PostgreSQL
    participant NAS as Synology NAS

    A->>UI: Voer definitief sitenummer in
    UI->>API: Vraag simulatie
    API->>N: Genereer migratieplan
    N-->>API: Oude en nieuwe naam per bestand
    API-->>UI: Toon plan en conflicten
    A->>UI: Start migratie
    UI->>Auth: Step-up authenticatie
    Auth-->>UI: Bevestigd
    UI->>API: Start definitieve migratie

    loop Eén bestand per stap
        API->>N: Genereer en reserveer naam
        API->>NAS: Hernoem binnen dezelfde SITE-map
        API->>NAS: Controleer hash
        API->>DB: Registreer resultaat
    end

    API->>DB: Activeer definitief sitenummer
    API-->>UI: Toon eindrapport
```

## 9. AI-validatie en feedback

```mermaid
flowchart TD
    Upload[Document of foto]
    OCR[OCR / Vision]
    Extract[Metadata en bevindingen]
    Proposal[AI-voorstel]
    Review{Validatieregels en confidence}
    Manual[Handmatige controle]
    Bulk[Bulkbevestiging]
    Sample[Steekproef]
    Confirm[Definitief bevestigen]
    Feedback[Menselijke correctie registreren]
    Improve[Prompts, regels of modellen verbeteren]

    Upload --> OCR --> Extract --> Proposal --> Review
    Review -- Laag / afwijkend --> Manual
    Review -- Hoog / toegestaan --> Bulk --> Sample
    Sample -- Afgekeurd --> Manual
    Sample -- Goedgekeurd --> Confirm
    Manual --> Confirm
    Confirm --> Feedback --> Improve
```

## 10. RAG- en kennisarchitectuur

```mermaid
flowchart LR
    Docs[Gevalideerde documenten]
    Corrections[Menselijke correcties]
    Standards[Normen en procedures]
    Chunk[Chunking + metadata]
    Embed[Embedding Service]
    Vector[(Vectorindex)]
    Graph[(Knowledge Graph)]
    Search[Hybride zoekservice]
    LLM[LLM]
    Answer[Antwoord met bronnen]

    Docs --> Chunk
    Corrections --> Chunk
    Standards --> Chunk
    Chunk --> Embed --> Vector
    Chunk --> Graph
    Vector --> Search
    Graph --> Search
    Search --> LLM --> Answer
```

## 11. Gecombineerde authenticatiestroom

```mermaid
flowchart TD
    Start[Gebruiker opent aanmelding]
    Policy[Lees organisatiebeleid]
    Choice{Toegestane methode}
    Password[Controleer wachtwoord]
    Passkey[Passkey-flow]
    TOTP[TOTP-flow]
    Recovery[Herstelcode]
    Verify{Verificatie geldig?}
    Session[Maak sessie / tokens]
    Deny[Weiger en registreer event]

    Start --> Policy --> Choice
    Choice -->|Wachtwoord + Passkey| Password --> Passkey
    Choice -->|Wachtwoord + TOTP| Password --> TOTP
    Choice -->|Wachtwoordloos| Passkey
    Choice -->|Noodherstel| Recovery
    Passkey --> Verify
    TOTP --> Verify
    Recovery --> Verify
    Verify -- Ja --> Session
    Verify -- Nee --> Deny
```

## 12. WebAuthn / Passkey-registratie

```mermaid
sequenceDiagram
    actor U as Gebruiker
    participant UI as Webfrontend
    participant API as Backend
    participant Redis as Challenge Store
    participant Auth as Platformauthenticator / Security key
    participant DB as PostgreSQL

    U->>UI: Kies Passkey toevoegen
    UI->>API: POST register/options
    API->>API: Controleer sessie en step-up
    API->>Redis: Bewaar eenmalige challenge
    API-->>UI: PublicKeyCredentialCreationOptions
    UI->>Auth: navigator.credentials.create()
    Auth->>U: Lokale verificatie met biometrie, PIN of aanraking
    Auth-->>UI: Attestation response
    UI->>API: POST register/verify
    API->>Redis: Lees en verbruik challenge
    API->>API: Valideer origin, RP ID en attestation
    API->>DB: Bewaar credential ID en publieke sleutel
    API->>DB: Registreer security- en audit-event
    API-->>UI: Passkey geregistreerd
```

De private sleutel en biometrische gegevens blijven op de authenticator.

## 13. Passkey-login

```mermaid
sequenceDiagram
    actor U as Gebruiker
    participant UI as Webfrontend
    participant API as Backend
    participant Redis as Challenge Store
    participant Auth as Platformauthenticator / Security key
    participant DB as PostgreSQL

    U->>UI: Kies Aanmelden met passkey
    UI->>API: POST login/options
    API->>Redis: Bewaar eenmalige challenge
    API-->>UI: PublicKeyCredentialRequestOptions
    UI->>Auth: navigator.credentials.get()
    Auth->>U: Lokale verificatie
    Auth-->>UI: Assertion + signature
    UI->>API: POST login/verify
    API->>Redis: Lees en verbruik challenge
    API->>DB: Lees publieke credential
    API->>API: Valideer origin, RP ID, signature en user verification
    API->>DB: Werk sign count en last_used_at bij
    API->>DB: Maak sessie en registreer event
    API-->>UI: Access- en refresh-token / sessie
```

## 14. TOTP-login

```mermaid
sequenceDiagram
    actor U as Gebruiker
    participant UI as Webfrontend
    participant API as Backend
    participant DB as PostgreSQL
    participant App as Authenticator-app

    U->>UI: E-mailadres en wachtwoord
    UI->>API: Login
    API->>DB: Controleer account en wachtwoordhash
    API-->>UI: TOTP vereist
    U->>App: Lees code
    U->>UI: Voer code in
    UI->>API: Verifieer TOTP
    API->>DB: Lees versleutelde TOTP-configuratie
    API->>API: Controleer code en voorkom hergebruik
    API->>DB: Registreer sessie en event
    API-->>UI: Aanmelding voltooid
```

## 15. Step-up authenticatie

```mermaid
sequenceDiagram
    actor U as Gebruiker
    participant UI as Webfrontend
    participant API as Backend
    participant Auth as Authenticatieservice
    participant DB as PostgreSQL

    U->>UI: Start gevoelige actie
    UI->>API: Voer actie uit
    API-->>UI: STEP_UP_REQUIRED
    UI->>Auth: Vraag step-up opties
    Auth-->>UI: Passkey of TOTP
    U->>UI: Bevestig aanvullende verificatie
    UI->>Auth: Verifieer Passkey / TOTP
    Auth->>DB: Registreer step-up tijdstip en event
    Auth-->>UI: Step-up geslaagd
    UI->>API: Herhaal oorspronkelijke actie
    API-->>UI: Actie uitgevoerd
```

## 16. Multi-device- en credentialbeheer

```mermaid
flowchart TB
    User[Gebruiker]
    SecurityPage[Beveiliging en aanmelden]
    Passkey1[Laptop - Windows Hello]
    Passkey2[Telefoon - Face ID / Android]
    Key[Security key]
    TOTP[Authenticator-app]
    Recovery[Herstelcodes]
    Sessions[Actieve sessies]
    Backend[Authenticatieservice]
    DB[(PostgreSQL)]

    User --> SecurityPage
    SecurityPage --> Passkey1
    SecurityPage --> Passkey2
    SecurityPage --> Key
    SecurityPage --> TOTP
    SecurityPage --> Recovery
    SecurityPage --> Sessions
    SecurityPage --> Backend --> DB
```

Beheerregels:

- Een gebruiker kan meerdere Passkeys registreren.
- Passkeys kunnen worden hernoemd en ingetrokken.
- Het verwijderen van de laatste bruikbare sterke authenticatiemethode wordt geblokkeerd.
- Credentialwijzigingen vereisen step-up authenticatie.
- Beveiligingswijzigingen kunnen bestaande sessies intrekken.

## 17. Autorisatiestroom

```mermaid
flowchart LR
    Request[API-verzoek]
    Session[Valideer sessie / token]
    Strength[Controleer authenticatieniveau]
    StepUp[Controleer recente step-up]
    Role[Controleer rol]
    Org[Controleer organisatiebereik]
    Site[Controleer Sitebereik]
    Permission[Controleer permissie]
    Allow[Toestaan]
    Deny[Weigeren en loggen]

    Request --> Session
    Session -- Ongeldig --> Deny
    Session -- Geldig --> Strength
    Strength -- Onvoldoende --> Deny
    Strength -- Voldoende --> StepUp
    StepUp -- Vereist en ontbreekt --> Deny
    StepUp -- OK / niet vereist --> Role
    Role --> Org --> Site --> Permission
    Permission -- Toegestaan --> Allow
    Permission -- Niet toegestaan --> Deny
```

## 18. Monitoring en security-events

```mermaid
flowchart LR
    Frontend[Frontend]
    Backend[Backend]
    Workers[Workers]
    Auth[Authenticatieservice]
    PostgreSQL[PostgreSQL]
    AI[AI-platform]
    NAS[NAS]
    Logs[Central Log Collector]
    Metrics[Metrics Collector]
    Dashboard[Monitoring Dashboard]
    Alert[Alerting]
    Admin[Beheerder]

    Frontend --> Logs
    Backend --> Logs
    Workers --> Logs
    Auth --> Logs
    PostgreSQL --> Metrics
    Backend --> Metrics
    Workers --> Metrics
    AI --> Metrics
    NAS --> Metrics
    Logs --> Dashboard
    Metrics --> Dashboard
    Logs --> Alert
    Metrics --> Alert
    Alert --> Admin
```

Te bewaken indicatoren:

- API-fouten en responstijd;
- actieve en falende jobs;
- AI-wachttijd en GPU-gebruik;
- PostgreSQL- en NAS-status;
- mislukte logins, TOTP-fouten en WebAuthn-fouten;
- verdachte credential- of sessiewijzigingen;
- openstaande validaties en migraties.

## 19. Back-up en herstel

```mermaid
flowchart TD
    DB[(PostgreSQL)]
    Files[(Documentopslag)]
    Dump[Databaseback-up]
    Snapshot[NAS-snapshot / bedrijfsback-up]
    Verify[Back-upverificatie]
    Restore[Testherstel]
    Report[Rapport en alerting]

    DB --> Dump --> Snapshot
    Files --> Snapshot
    Snapshot --> Verify --> Restore --> Report
```

Encryptiesleutels voor TOTP-geheimen worden niet samen met de databaseback-up opgeslagen.

## 20. Release en rollback

```mermaid
flowchart LR
    Git[Git Repository]
    CI[Lint, tests en security checks]
    Images[Versiegebonden container-images]
    Test[Testomgeving]
    Accept[Acceptatie]
    Backup[Verplichte back-up]
    Prod[Productie-uitrol]
    Health[Health checks]
    Decision{Gezond?}
    Complete[Voltooid]
    Rollback[Rollback]

    Git --> CI --> Images --> Test --> Accept --> Backup --> Prod --> Health --> Decision
    Decision -- Ja --> Complete
    Decision -- Nee --> Rollback
```

## 21. Bevestigde architectuurbeslissingen

- React/TypeScript frontend met FastAPI backend.
- PostgreSQL als centrale bron van waarheid.
- Redis voor queues, locks en tijdelijke WebAuthn-challenges.
- Synology NAS als fysieke documentopslag.
- Centrale Naamgevingsservice en verplichte sequentiële bestandsverwerking.
- Onveranderlijke fysieke `storage_code` per Site.
- On-prem AI-platform op de HPE ML350 met 3 x RTX 3090.
- Sterke authenticatie via TOTP en WebAuthn/Passkeys.
- Passkeys zijn de aanbevolen authenticatiemethode.
- Wachtwoordloze en usernameless login zijn configureerbaar.
- Biometrische gegevens worden niet door de applicatie opgeslagen.
- Step-up authenticatie beschermt gevoelige acties.
- Meerdere Passkeys en actieve sessies zijn per gebruiker beheersbaar.
- Herstelcodes worden eenmalig gebruikt en gehasht opgeslagen.
- Geen automatische SharePoint-integratie.

## 22. Openstaande technische keuzes

- Definitieve RP ID en toegestane origins per omgeving.
- Attestationbeleid en eventuele AAGUID-allowlist.
- JWT in headers of beveiligde sessiecookies.
- Exacte geldigheidsduur van challenges, sessies en step-up bevestigingen.
- Celery of RQ.
- NFS of SMB voor NAS-toegang.
- Definitieve monitoringstack.
- Strategie voor hoge beschikbaarheid.

## 23. Relatie met andere ontwerpdocumenten

| Document | Relatie |
|---|---|
| `01_Functioneel_Ontwerp.md` | Functionele eisen en processen |
| `02_Technisch_Ontwerp.md` | Technische architectuur en beveiliging |
| `03_Database_Ontwerp.md` | Tabellen, credentials, sessies en constraints |
| `04_AI_Knowledge_Platform_Ontwerp.md` | AI-, RAG- en kennisarchitectuur |
| `05_API_Ontwerp.md` | REST-, WebAuthn- en step-up-endpoints |
| `06_Deployment_Infrastructuur.md` | Infrastructuur, netwerk en back-up |
| `07_UI_UX_Ontwerp.md` | Aanmeldschermen en credentialbeheer |
| `08_Architectuur_Diagrammen.md` | Visuele samenhang van alle onderdelen |
