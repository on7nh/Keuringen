# Deployment & Infrastructuur Ontwerp

## Digitaal Keurings- en Documentbeheer

**Versie:** 1.0 Concept  
**Status:** Uitgewerkt technisch ontwerp

## 1. Doel

Dit document beschrijft de doelarchitectuur voor hosting, netwerk, beveiliging, opslag, back-up, monitoring, GPU-verwerking en operationeel beheer van het platform.

De infrastructuur wordt ontworpen als een lokale, beheersbare en uitbreidbare omgeving. De documentapplicatie en het AI-platform blijven logisch gescheiden, maar werken via gecontroleerde interne interfaces samen.

## 2. Ontwerpprincipes

- Local-first en zonder verplichte externe clouddiensten
- Scheiding tussen gebruikersverkeer, applicatieverkeer, beheer en AI-verkeer
- Geen directe toegang van clients tot PostgreSQL, Redis, NAS of modelservers
- Containerized deployment voor applicatiediensten
- Reproduceerbare configuratie via versiebeheer
- Minimaal één herstelbaar back-uppad voor database, documenten en configuratie
- Monitoring van beschikbaarheid, capaciteit, beveiliging en AI-kwaliteit
- Horizontale uitbreiding mogelijk voor web-, worker- en AI-services
- Productie, test en ontwikkeling logisch gescheiden
- Least privilege voor netwerk, services en gebruikers

## 3. Logische infrastructuurlagen

```text
Gebruikersnetwerk
   |
   v
Reverse Proxy / TLS
   |
   v
Frontend + Backend API
   |
   +--> PostgreSQL
   +--> Redis / Queue
   +--> NAS Documentopslag
   +--> Monitoring
   +--> Interne AI Gateway
              |
              +--> OCR
              +--> Vision
              +--> LLM
              +--> Embeddings
              +--> Training / Evaluatie
```

## 4. Omgevingen

### 4.1 Productie

Bevat de bedrijfsgegevens en actieve AI-modellen. Toegang is beperkt tot bevoegde gebruikers en beheerders.

### 4.2 Test

Bevat synthetische of geanonimiseerde gegevens. Wordt gebruikt voor releases, migraties, promptwijzigingen en modeltests.

### 4.3 Ontwikkeling

Lokale ontwikkelomgeving met Docker Compose en voorbeelddata. Geen productiegeheimen of productieback-ups.

## 5. Voorgestelde serverrollen

### 5.1 Applicatiehost

Draait minimaal:

- Reverse proxy
- Frontend
- Backend API
- Background workers
- Redis
- Monitoring exporters

PostgreSQL kan in de eerste fase op dezelfde virtualisatiehost draaien, maar wordt als afzonderlijke VM of containerstack beheerd.

### 5.2 Databasehost

- PostgreSQL
- pgvector indien geactiveerd
- Back-upagent
- Monitoring exporter
- Geen publieke netwerktoegang

### 5.3 AI-server

HPE ProLiant ML350 met:

- 346 GiB RAM
- 3 x NVIDIA RTX 3090
- Initieel 2 x Xeon Silver 4110
- Later 2 x Xeon Gold 6258R

Draait:

- AI Gateway
- Modelserver(s)
- OCR-service
- Vision-service
- Embedding-service
- AI-jobworkers
- Evaluatie- en trainingservices
- GPU-monitoring

### 5.4 Synology NAS

Dient voor:

- Definitieve documentopslag
- PostgreSQL-back-ups
- Configuratieback-ups
- Modeladapters en evaluatie-artifacts
- Herstelkopieën volgens retentiebeleid

## 6. Virtualisatie

Proxmox VE wordt aanbevolen voor de applicatie- en databaseomgeving.

Voorgestelde VM's:

```text
vm-proxy-prod
vm-app-prod
vm-db-prod
vm-monitoring
vm-app-test
vm-db-test
```

De AI-server kan bare-metal Linux draaien om GPU-complexiteit te beperken. Virtualisatie van de AI-server blijft mogelijk, maar GPU-passthrough verhoogt beheer- en storingscomplexiteit.

## 7. Besturingssystemen

Aanbevolen basis:

- Debian 12 of opvolgende stabiele LTS-geschikte release
- Alleen noodzakelijke packages
- Automatische beveiligingsupdates waar veilig
- Geplande onderhoudsvensters voor kernel-, NVIDIA- en containerupdates
- Tijdssynchronisatie via interne of betrouwbare NTP-bron

## 8. Containerstrategie

Docker Compose is geschikt voor de eerste productiefase.

Voorbeeldstacks:

```text
stack-edge
  - reverse-proxy
  - certificate-management

stack-app
  - frontend
  - api
  - worker-default
  - worker-upload
  - worker-reporting
  - redis

stack-data
  - postgres
  - backup-agent

stack-ai
  - ai-gateway
  - llm-server
  - vision-server
  - embedding-server
  - ocr-worker
  - ai-workers

stack-observability
  - prometheus
  - grafana
  - loki
  - alertmanager
```

Containers gebruiken vaste imageversies; `latest` is niet toegestaan in productie.

## 9. Netwerksegmentatie

Aanbevolen zones:

- User VLAN
- Application VLAN
- Database VLAN
- AI VLAN
- Storage VLAN
- Management VLAN
- Backup VLAN indien beschikbaar

Belangrijke regels:

- User VLAN mag alleen reverse proxy bereiken
- Applicatiehost mag PostgreSQL, Redis, NAS en AI Gateway bereiken
- Databasehost accepteert alleen verkeer van applicatie- en beheernetwerk
- AI-modelservers accepteren alleen verkeer van AI Gateway
- NAS accepteert alleen noodzakelijke protocollen vanaf specifieke hosts
- Managementinterfaces zijn alleen bereikbaar vanuit beheer-VLAN of VPN

## 10. Reverse proxy en TLS

De reverse proxy verzorgt:

- HTTPS-terminatie
- Veilige headers
- Request size-limieten
- Rate limiting
- Routing naar frontend en API
- Optioneel client-IP-registratie

TLS-certificaten worden intern of via een geschikte certificaatautoriteit uitgegeven. Interne servicecommunicatie gebruikt waar mogelijk eveneens TLS.

## 11. Opslagarchitectuur

### 11.1 Documentopslag

Bestanden worden buiten PostgreSQL opgeslagen in een gecontroleerde directorystructuur.

Voorbeeld:

```text
/documents/{organization_id}/{site_id}/{document_id}/{version_id}/bestand.ext
```

Eigenschappen:

- Applicatie bepaalt de definitieve bestandsnaam
- Originele bestandsnaam blijft metadata
- SHA-256-hash wordt opgeslagen
- Bestaande bestanden worden niet stilzwijgend overschreven
- Tijdelijke uploads blijven gescheiden van definitieve opslag
- Quarantaine voor onvolledig gevalideerde bestanden

### 11.2 AI-opslag

- Basismodellen op lokale snelle opslag van de AI-server
- Modelcache niet op trage NAS voor actieve inferentie
- Adapters, prompts en evaluatieresultaten op back-upbare opslag
- Trainingsdatasets logisch gescheiden van productiegegevens

### 11.3 Capaciteitsplanning

Maandelijks worden gecontroleerd:

- Groei documentopslag
- Groei database
- Groei embeddings
- Grootte logs
- Grootte modellen en datasets
- Vrije ruimte op lokale SSD/NVMe en NAS

Waarschuwingsdrempels worden ingesteld op 70%, 85% en 95%.

## 12. PostgreSQL-deployment

Aanbevolen instellingen:

- Afzonderlijke databasegebruiker per service
- Geen superuser voor applicatie
- Versleutelde verbindingen
- Regelmatige VACUUM/ANALYZE
- Monitoring van locks, trage queries en verbindingen
- Connection pooling
- Migraties via Alembic
- Back-up vóór iedere destructieve migratie

## 13. Redis en jobwachtrijen

Redis ondersteunt:

- Achtergrondjobs
- Tijdelijke status
- Rate limiting
- Eventuele caching

Redis is geen bron van waarheid. Verlies van Redis mag niet leiden tot verlies van definitief bevestigde bedrijfsgegevens.

Prioriteitswachtrijen:

```text
critical
interactive
normal
batch
training
```

## 14. AI-deployment

### 14.1 GPU-verdeling

Eerste uitgangspunt:

- GPU 0: productie-LLM
- GPU 1: vision en GPU-OCR
- GPU 2: batch, embeddings, evaluatie en gecontroleerde training

De verdeling is configureerbaar.

### 14.2 NVIDIA-stack

- NVIDIA-driver als hostcomponent
- NVIDIA Container Toolkit
- Geteste combinatie van driver, CUDA-runtime en modelserver
- Wijzigingen eerst in test
- GPU-healthcheck na iedere update

### 14.3 Resourcebeperking

Per container:

- CPU- en RAM-limieten
- GPU-toewijzing
- Maximum aantal gelijktijdige jobs
- Timeout
- Restart policy
- Healthcheck

### 14.4 Modelpromotie

Modelversies doorlopen:

1. Installatie in test
2. Technische healthcheck
3. Evaluatie op vaste dataset
4. Goedkeuring
5. Productieactivatie
6. Monitoring
7. Mogelijke rollback

## 15. Beveiliging

### 15.1 Hostbeveiliging

- SSH alleen met sleutels
- Geen rechtstreekse rootlogin
- Firewall per host
- Audit van beheeracties
- Beperkte sudo-rechten
- Regelmatige patchcyclus
- Onnodige services uitgeschakeld

### 15.2 Secrets

Geheimen worden niet in Git opgeslagen.

Minimaal:

- Databasewachtwoorden
- JWT- of sessiesleutels
- TOTP-encryptiesleutel
- NAS-credentials
- interne API-sleutels
- TLS-private keys

Een secretsmanager is wenselijk. In de eerste fase kunnen streng beveiligde environment-files worden gebruikt met beperkte bestandsrechten.

### 15.3 Bestandsbeveiliging

- MIME- en extensiecontrole
- Bestandsgroottecontrole
- Malwarecontrole indien beschikbaar
- Quarantaine bij twijfel
- Geen automatische uitvoering van uploads
- DWG en XLSX alleen als gegevensbestand behandelen

## 16. Monitoring

### 16.1 Technische metrics

- Beschikbaarheid services
- CPU, RAM, disk en netwerk
- PostgreSQL-connections en queryduur
- Redis-wachtrijen
- HTTP-fouten en latency
- Uploadduur
- Workerstatus
- NAS-bereikbaarheid

### 16.2 AI-metrics

- GPU-gebruik en temperatuur
- VRAM-gebruik
- Model-laadtijd
- Tokens per seconde
- Jobwachttijd
- Foutpercentage
- Timeouts en retries
- Correctiepercentage per model en prompt

### 16.3 Logging

Logs bevatten:

- timestamp
- service
- severity
- correlation-id
- actor-id waar toegestaan
- gebeurteniscode

Geen wachtwoorden, tokens, TOTP-geheimen of volledige gevoelige documenten.

## 17. Alerting

Voorbeelden van kritieke alerts:

- Applicatie of database onbereikbaar
- Back-up mislukt
- NAS niet bereikbaar
- Schijfgebruik boven 90%
- PostgreSQL-replicatie of back-upachterstand indien van toepassing
- GPU boven veilige temperatuur
- AI-jobwachtrij loopt langdurig op
- Herhaaldelijke authenticatiefouten
- Certificaat verloopt binnen 30 dagen

Alerts worden geclassificeerd als informatief, waarschuwing of kritiek.

## 18. Back-upstrategie

### 18.1 PostgreSQL

- Dagelijkse logische of fysieke back-up
- Extra back-up vóór release of migratie
- Retentie met dagelijkse, wekelijkse en maandelijkse kopieën
- Periodieke restoretest

### 18.2 Documenten

- NAS-snapshots
- Versiebehoud waar ondersteund
- Periodieke kopie naar een afzonderlijk opslagdoel
- Hashcontrole bij hersteltests

### 18.3 Applicatieconfiguratie

Back-up van:

- Compose-bestanden
- Reverse proxy-configuratie
- Environment-template zonder geheimen
- Migraties
- Monitoringconfiguratie
- Promptversies
- Kennisregels
- Modelmetadata

### 18.4 AI-artifacts

Basismodellen kunnen opnieuw worden verkregen wanneer licentie en bron dit toelaten. Eigen adapters, evaluatiesets, prompts en trainingsmetadata zijn bedrijfskritiek en worden wel geback-upt.

## 19. Disaster Recovery

### 19.1 Herstelprioriteit

1. Netwerk en virtualisatie
2. PostgreSQL
3. Documentopslag
4. Backend API
5. Frontend
6. Jobverwerking
7. AI-platform
8. Rapportering en secundaire functies

### 19.2 Indicatieve doelstellingen

- RPO database: maximaal 24 uur in eerste fase
- RTO kernapplicatie: één werkdag in eerste fase
- AI-verwerking mag tijdelijk later hersteld worden dan documentraadpleging

Deze waarden moeten door de organisatie formeel worden goedgekeurd.

### 19.3 Restoreprocedure

- Nieuwe of herstelde VM voorbereiden
- Configuratie uit versiebeheer ophalen
- Geheimen veilig herstellen
- PostgreSQL terugzetten
- NAS-mount valideren
- Migratieversie controleren
- Applicatie starten
- Integriteits- en functionele checks uitvoeren
- AI-platform afzonderlijk valideren

## 20. Release- en updateproces

1. Wijziging ontwikkelen
2. Automatische tests
3. Image build en security scan
4. Deployment naar test
5. Database-migratietest
6. Functionele acceptatie
7. Back-up productie
8. Productiedeployment
9. Healthchecks
10. Smoke tests
11. Monitoring
12. Rollback indien nodig

## 21. Rollback

Iedere release bevat:

- Vorige containerimages
- Databaseherstelplan
- Achterwaarts compatibele migraties waar mogelijk
- Feature flags voor risicovolle functies
- Gedocumenteerde rollbackbeslissing

## 22. Operationele procedures

Te documenteren runbooks:

- Applicatie herstarten
- Workerwachtrij vrijmaken
- Vastgelopen AI-job behandelen
- NAS-storing
- Databaseherstel
- Certificaatvernieuwing
- Gebruiker blokkeren
- Model rollback
- Schijfruimte vrijmaken
- Incidentregistratie

## 23. Schaalbaarheid

Eerste uitbreidingspaden:

- Meerdere API-instances achter reverse proxy
- Extra workers per jobtype
- Aparte PostgreSQL-host
- Read replica voor rapportering
- Extra AI-server of GPU-node
- Gescheiden vectordatabase
- Object storage als alternatief voor traditionele fileshares

## 24. Acceptatiecriteria infrastructuur

De productieomgeving is gereed wanneer:

- Alle services reproduceerbaar kunnen worden uitgerold
- Netwerkregels zijn getest
- Back-up en restore aantoonbaar werken
- Monitoring en alerts actief zijn
- Geen productiegeheimen in Git staan
- Upload van 100 MB betrouwbaar werkt
- AI-uitval de kernapplicatie niet onbruikbaar maakt
- Audit- en beveiligingscontroles aantoonbaar zijn uitgevoerd

## 25. Openstaande keuzes

- Definitieve Proxmox-topologie
- Bare-metal of virtuele AI-server
- Exacte reverse proxy
- Secretsmanager
- Malware-scanner
- Monitoringstack
- Off-site back-updoel
- Definitieve RPO en RTO
- Opslagprotocol tussen applicatie en Synology NAS
- Eventuele PostgreSQL high availability
