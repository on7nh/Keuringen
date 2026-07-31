# Installatie Website op Debian 12

## Digitaal Keurings- en Documentbeheer

**Documentnummer:** 20  
**Versie:** 1.2 Concept  
**Doelplatform:** Debian 12 VM  
**Applicatiepoort:** TCP 8080  
**Repository:** `on7nh/Keuringen`

## 1. Doel

Dit document beschrijft de installatie van de webapplicatie op een Debian 12 virtuele machine.

De vaste webarchitectuur is:

- React voor de gebruikersinterface;
- FastAPI voor de backend, API en het aanbieden van de React-build;
- Uvicorn of Gunicorn met Uvicorn workers als ASGI-server;
- Docker Compose voor deployment;
- Redis voor queues en tijdelijke data;
- afzonderlijke worker- en schedulerprocessen;
- een afzonderlijke PostgreSQL-server;
- Synology NAS voor documentopslag;
- het on-prem AI-platform voor OCR, Vision, LLM, STT en RAG.

De volledige website, API en health endpoints worden via één applicatiecontainer gepubliceerd op:

```text
0.0.0.0:8080/tcp
```

Na installatie is de applicatie intern bereikbaar via:

```text
http://<IP-ADRES-VAN-DE-VM>:8080
```

Voor productie wordt HTTPS via een centrale reverse proxy of load balancer aanbevolen. De Debian VM blijft intern op poort 8080 luisteren.

## 2. Vastgelegde architectuurkeuzes

### 2.1 Geen Django

Django wordt niet geïnstalleerd en maakt geen deel uit van deze architectuur.

Het project gebruikt FastAPI als backendframework en React als frontend. Django daarnaast toevoegen zou een tweede backendframework introduceren met overlappende verantwoordelijkheden voor onder meer routing, authenticatie, middleware, ORM en sessiebeheer.

De vaste keuze is daarom:

```text
React + FastAPI
```

Niet:

```text
React + Django + FastAPI
```

### 2.2 Geen verplichte Nginx op de applicatie-VM

Nginx wordt niet standaard op de Debian 12 VM geïnstalleerd.

FastAPI biedt zowel de API als de gecompileerde React-build aan. Daardoor is er op de VM slechts één publiek ingangspunt nodig.

```text
Browser
   |
   | TCP 8080
   v
FastAPI / ASGI
   |- React static files
   |- REST API
   |- SSE endpoints
   `- Health endpoints
```

Nginx kan later optioneel worden toegevoegd wanneer daar een concrete noodzaak voor bestaat, bijvoorbeeld lokale TLS-terminatie, meerdere applicaties op dezelfde VM of complexe proxyregels. Dit is geen onderdeel van de standaardinstallatie.

### 2.3 React wordt altijd door FastAPI aangeboden

De React-applicatie wordt tijdens de containerbuild gecompileerd. Het resultaat wordt in de uiteindelijke applicatie-image geplaatst en door FastAPI als statische bestanden aangeboden.

Er is dus:

- geen afzonderlijke frontendcontainer;
- geen afzonderlijke Nginx-container;
- geen tweede publiek webproces;
- geen aparte hostpoort voor de frontend.

Deze keuze levert één uniforme release-eenheid op en voorkomt versieverschillen tussen frontend en backend.

## 3. Doelarchitectuur

```text
Gebruiker
   |
   | HTTPS 443
   v
Centrale reverse proxy / load balancer
   |
   | HTTP 8080 in intern netwerk
   v
Debian 12 VM
   |
   `- Docker Compose
       |- web: FastAPI + React-build
       |- worker
       |- scheduler
       `- Redis

Externe verbindingen:
   |- PostgreSQL
   |- Synology NAS
   |- AI Gateway
   `- SMTP
```

Voor een testomgeving kan rechtstreeks naar de VM worden gegaan:

```text
Gebruiker -> http://<VM-IP>:8080
```

Voor productie:

```text
Gebruiker -> https://keuringen.intern.example -> reverse proxy -> http://<VM-IP>:8080
```

## 4. Aanbevolen VM-specificaties

| Onderdeel | Aanbeveling |
|---|---:|
| Besturingssysteem | Debian 12 64-bit |
| CPU | 4 vCPU |
| RAM | 8 GiB |
| Systeemschijf | 80 GiB |
| Netwerk | Vast IP-adres |
| Tijdzone | Europe/Brussels |
| DNS | Interne DNS-resolutie |

## 5. Netwerkverbindingen

### 5.1 Inkomend

| Bron | Doelpoort | Protocol | Doel |
|---|---:|---|---|
| Gebruikersnetwerk of centrale reverse proxy | 8080 | TCP | Website en API |
| Beheerzone | 22 | TCP | SSH-beheer |

### 5.2 Uitgaand

| Doel | Poort | Gebruik |
|---|---:|---|
| PostgreSQL-server | 5432/TCP | Database |
| Synology NAS | 2049/TCP of 445/TCP | NFS of SMB |
| AI Gateway | 443/TCP of afgesproken poort | AI-diensten |
| SMTP-server | 25, 465 of 587/TCP | E-mailnotificaties |
| DNS | 53/TCP en UDP | Naamresolutie |
| NTP | 123/UDP | Tijdsynchronisatie |
| GitHub of interne Git-server | 443/TCP | Installatie en updates |
| Debian repositories | 80 en 443/TCP | Systeempakketten |

Open uitsluitend verbindingen die werkelijk nodig zijn.

## 6. Debian 12 voorbereiden

Controleer het besturingssysteem:

```bash
cat /etc/os-release
uname -a
```

Werk het systeem bij:

```bash
sudo apt update
sudo apt full-upgrade -y
sudo apt autoremove -y
```

Installeer basispakketten:

```bash
sudo apt install -y \
  ca-certificates \
  curl \
  git \
  gnupg \
  jq \
  openssl \
  rsync \
  ufw \
  unzip
```

Stel tijdzone en tijdsynchronisatie in:

```bash
sudo timedatectl set-timezone Europe/Brussels
sudo timedatectl set-ntp true
timedatectl status
```

Een correcte systeemtijd is noodzakelijk voor JWT, TOTP en WebAuthn.

## 7. Vast IP-adres en DNS

Voorbeeld:

```text
Hostnaam: keuringen-web01
FQDN: keuringen-web01.intern.example
IP-adres: 192.168.10.40
Gateway: 192.168.10.1
DNS: 192.168.10.10
```

Stel de hostnaam in:

```bash
sudo hostnamectl set-hostname keuringen-web01
```

Controleer naamresolutie:

```bash
hostname -f
getent hosts keuringen-web01.intern.example
```

## 8. Beheeraccount en SSH

Maak indien nodig een beheeraccount:

```bash
sudo adduser keuringen-admin
sudo usermod -aG sudo keuringen-admin
```

Gebruik SSH-sleutels. Voorbeeld `/etc/ssh/sshd_config.d/keuringen.conf`:

```text
PermitRootLogin no
PasswordAuthentication no
PubkeyAuthentication yes
```

Valideer en herlaad SSH:

```bash
sudo sshd -t
sudo systemctl reload ssh
```

Test eerst een nieuwe SSH-sessie voordat de bestaande sessie wordt gesloten.

## 9. Docker Engine en Docker Compose installeren

Verwijder conflicterende pakketten:

```bash
sudo apt remove -y docker.io docker-doc docker-compose podman-docker containerd runc || true
```

Voeg de officiële Docker repository toe:

```bash
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/debian/gpg \
  | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg
```

```bash
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian \
  $(. /etc/os-release && echo \"$VERSION_CODENAME\") stable" \
  | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
```

Installeer Docker:

```bash
sudo apt update
sudo apt install -y \
  docker-ce \
  docker-ce-cli \
  containerd.io \
  docker-buildx-plugin \
  docker-compose-plugin
```

Activeer en controleer Docker:

```bash
sudo systemctl enable --now docker
sudo docker version
sudo docker compose version
sudo docker run --rm hello-world
```

Voeg alleen bevoegde beheerders toe aan de Docker-groep:

```bash
sudo usermod -aG docker "$USER"
```

## 10. Repository installeren

```bash
sudo mkdir -p /opt/keuringen
sudo chown "$USER":"$USER" /opt/keuringen
cd /opt/keuringen
git clone https://github.com/on7nh/Keuringen.git app
cd app
git checkout main
git status
git log -1 --oneline
```

Gebruik voor een private repository een goedgekeurde deploy key of GitHub App-authenticatie. Plaats geen toegangstokens in scripts of shell history.

## 11. Persistente mappen

```bash
sudo mkdir -p /opt/keuringen/data/redis
sudo mkdir -p /opt/keuringen/data/uploads
sudo mkdir -p /opt/keuringen/data/logs
sudo mkdir -p /opt/keuringen/secrets
sudo chown -R root:root /opt/keuringen/secrets
sudo chmod 700 /opt/keuringen/secrets
```

Documentbestanden horen op de Synology NAS te staan en niet uitsluitend op de lokale VM.

## 12. Synology NAS koppelen

### 12.1 NFS

```bash
sudo apt install -y nfs-common
sudo mkdir -p /mnt/keuringen-documents
sudo mount -t nfs <NAS-IP>:/volume1/keuringen /mnt/keuringen-documents
```

Voorbeeld `/etc/fstab`:

```text
<NAS-IP>:/volume1/keuringen /mnt/keuringen-documents nfs4 rw,hard,noatime,_netdev 0 0
```

Test:

```bash
sudo umount /mnt/keuringen-documents
sudo mount -a
findmnt /mnt/keuringen-documents
```

Gebruik geen `soft` NFS-mount voor documentopslag.

### 12.2 SMB

```bash
sudo apt install -y cifs-utils
sudo install -m 600 /dev/null /root/.keuringen-smb-credentials
sudo nano /root/.keuringen-smb-credentials
```

Voorbeeldinhoud:

```text
username=<serviceaccount>
password=<sterk-wachtwoord>
domain=<optioneel-domein>
```

Voorbeeld `/etc/fstab`:

```text
//<NAS-IP>/keuringen /mnt/keuringen-documents cifs credentials=/root/.keuringen-smb-credentials,vers=3.1.1,iocharset=utf8,nosuid,nodev,_netdev 0 0
```

## 13. Omgevingsvariabelen

```bash
cd /opt/keuringen/app
cp .env.example .env
chmod 600 .env
nano .env
```

Voorbeeld:

```dotenv
APP_ENV=production
APP_HOST=0.0.0.0
APP_PORT=8080
PUBLIC_BASE_URL=http://keuringen-web01.intern.example:8080

POSTGRES_HOST=<DATABASE-IP-OF-DNS>
POSTGRES_PORT=5432
POSTGRES_DB=keuringen
POSTGRES_USER=keuringen_app
POSTGRES_PASSWORD=<STERK-UNIEK-WACHTWOORD>

REDIS_URL=redis://redis:6379/0
DOCUMENT_STORAGE_PATH=/data/documents
AI_GATEWAY_URL=https://<AI-GATEWAY-DNS>

JWT_SECRET=<MINSTENS-32-WILLEKEURIGE-BYTES>
JWT_ACCESS_TOKEN_MINUTES=15
JWT_REFRESH_TOKEN_DAYS=7

WEBAUTHN_RP_ID=keuringen-web01.intern.example
WEBAUTHN_ORIGIN=http://keuringen-web01.intern.example:8080
```

Genereer secrets bijvoorbeeld met:

```bash
openssl rand -base64 48
```

Voor productie moeten `PUBLIC_BASE_URL` en `WEBAUTHN_ORIGIN` naar de definitieve HTTPS-URL verwijzen.

## 14. React-build opnemen in de FastAPI-image

De applicatie-image wordt als multi-stage build samengesteld.

### 14.1 Voorbeeld Dockerfile

```dockerfile
FROM node:22-alpine AS frontend-build
WORKDIR /frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

FROM python:3.12-slim AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN addgroup --system app && adduser --system --ingroup app app

COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ ./
COPY --from=frontend-build /frontend/dist ./frontend-dist

RUN chown -R app:app /app
USER app

EXPOSE 8080

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
```

Pas de mapnamen aan de werkelijke repositorystructuur aan.

De build faalt wanneer de React-build niet kan worden gemaakt. Daardoor kan geen backendrelease zonder bijbehorende frontend worden uitgerold.

## 15. FastAPI-configuratie voor React

FastAPI registreert eerst alle API-, event- en healthroutes. Daarna worden de React-assets en de client-side routing fallback toegevoegd.

Voorbeeld:

```python
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI()

DIST_DIR = Path(__file__).resolve().parent.parent / "frontend-dist"
ASSETS_DIR = DIST_DIR / "assets"

# Registreer hier eerst alle API-routes.
# app.include_router(api_router, prefix="/api/v1")

if ASSETS_DIR.exists():
    app.mount("/assets", StaticFiles(directory=ASSETS_DIR), name="assets")

@app.get("/health", include_in_schema=False)
def health() -> dict[str, str]:
    return {"status": "ok"}

@app.get("/{full_path:path}", include_in_schema=False)
def react_fallback(full_path: str):
    requested = (DIST_DIR / full_path).resolve()

    if DIST_DIR.resolve() not in requested.parents and requested != DIST_DIR.resolve():
        raise HTTPException(status_code=404)

    if full_path and requested.is_file():
        return FileResponse(requested)

    index_file = DIST_DIR / "index.html"
    if not index_file.is_file():
        raise HTTPException(status_code=503, detail="Frontend build ontbreekt")

    return FileResponse(index_file)
```

Belangrijke regels:

- API-routes worden vóór de catch-all route geregistreerd;
- `/api`, `/health` en `/events` mogen nooit naar `index.html` vallen;
- alleen bestanden binnen de React-buildmap worden aangeboden;
- ontbrekende React-build resulteert in een duidelijke fout;
- de productie-image bevat geen Node.js-runtime.

## 16. ASGI-server

Voor een eenvoudige installatie:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8080
```

Voor productie kan Gunicorn worden gebruikt:

```bash
gunicorn app.main:app \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8080 \
  --workers 4 \
  --timeout 300
```

Het exacte modulepad en het aantal workers worden afgestemd op de uiteindelijke repository en beschikbare CPU-capaciteit.

## 17. Docker Compose

```yaml
services:
  web:
    build:
      context: .
    restart: unless-stopped
    ports:
      - "8080:8080"
    env_file:
      - .env
    environment:
      APP_HOST: 0.0.0.0
      APP_PORT: 8080
    volumes:
      - /mnt/keuringen-documents:/data/documents
    depends_on:
      redis:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8080/health')"]
      interval: 30s
      timeout: 5s
      retries: 5
      start_period: 30s

  worker:
    build:
      context: .
    restart: unless-stopped
    env_file:
      - .env
    command: ["python", "-m", "app.worker"]
    volumes:
      - /mnt/keuringen-documents:/data/documents
    depends_on:
      redis:
        condition: service_healthy

  scheduler:
    build:
      context: .
    restart: unless-stopped
    env_file:
      - .env
    command: ["python", "-m", "app.scheduler"]
    depends_on:
      redis:
        condition: service_healthy

  redis:
    image: redis:7-alpine
    restart: unless-stopped
    command: ["redis-server", "--appendonly", "yes"]
    volumes:
      - /opt/keuringen/data/redis:/data
    expose:
      - "6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 5
```

Belangrijke regels:

- alleen `web` publiceert een hostpoort;
- de enige hostpoort is `8080`;
- React en FastAPI zitten in dezelfde `web`-image;
- Redis wordt niet met `ports` gepubliceerd;
- PostgreSQL wordt niet vanuit deze VM gepubliceerd;
- workers en scheduler publiceren geen poorten;
- de NAS-map wordt alleen gekoppeld aan services die documenttoegang nodig hebben.

## 18. Firewall configureren met UFW

Open eerst SSH voor de beheerzone.

```bash
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow from 192.168.20.0/24 to any port 22 proto tcp comment 'SSH beheerzone'
sudo ufw allow from 192.168.10.0/24 to any port 8080 proto tcp comment 'Keuringen website'
sudo ufw enable
sudo ufw status verbose
```

Wanneer alleen een centrale reverse proxy toegang mag hebben:

```bash
sudo ufw delete allow from 192.168.10.0/24 to any port 8080 proto tcp
sudo ufw allow from <REVERSE-PROXY-IP> to any port 8080 proto tcp comment 'Reverse proxy naar Keuringen'
```

Gebruik alleen bij een bewuste keuze:

```bash
sudo ufw allow 8080/tcp
```

Dit opent poort 8080 voor alle bronnen en wordt voor een interne bedrijfsapplicatie niet aanbevolen.

### 18.1 Docker en UFW

Docker beheert eigen iptables-regels. Beperk de binding daarom zo mogelijk tot het interne VM-adres:

```yaml
ports:
  - "192.168.10.40:8080:8080"
```

Controleer daarnaast de Proxmox- en centrale netwerkfirewall.

## 19. Proxmox-firewall

| Richting | Actie | Bron of doel | Poort | Protocol |
|---|---|---|---:|---|
| IN | ACCEPT | Beheerzone | 22 | TCP |
| IN | ACCEPT | Gebruikersnetwerk of reverse proxy | 8080 | TCP |
| IN | DROP | Overig | alle | alle |
| OUT | ACCEPT | PostgreSQL-server | 5432 | TCP |
| OUT | ACCEPT | Synology NAS | 2049 of 445 | TCP |
| OUT | ACCEPT | AI Gateway | afgesproken poort | TCP |
| OUT | ACCEPT | DNS, NTP, SMTP en repositories | benodigde poorten | TCP/UDP |

Voer firewallwijzigingen uit terwijl consoletoegang tot de VM beschikbaar is.

## 20. Applicatie bouwen en starten

```bash
cd /opt/keuringen/app
docker compose config
docker compose build --pull
docker compose up -d
```

Controleer:

```bash
docker compose ps
docker compose logs --tail=100
docker compose logs --tail=100 web
```

## 21. Poort 8080 controleren

```bash
sudo ss -lntp | grep ':8080'
curl -I http://127.0.0.1:8080
curl -I http://<VM-IP>:8080
curl --fail http://127.0.0.1:8080/health
```

Verwacht luisteradres:

```text
LISTEN 0 4096 0.0.0.0:8080 0.0.0.0:*
```

Controleer ook dat een React-route werkt:

```bash
curl -I http://127.0.0.1:8080/
curl -I http://127.0.0.1:8080/login
```

## 22. Health checks

Voorzie minimaal:

```text
GET /health
GET /api/v1/health
GET /api/v1/health/ready
```

Een readiness-check controleert minimaal:

- FastAPI-proces;
- aanwezigheid van de React-build;
- PostgreSQL-verbinding;
- Redis-verbinding;
- schrijfrechten op documentopslag;
- bereikbaarheid van verplichte interne diensten.

## 23. HTTPS en Passkeys

De applicatie blijft intern op poort 8080 luisteren.

```text
Gebruiker
   |
   | HTTPS 443
   v
Centrale reverse proxy / load balancer
   |
   | HTTP 8080
   v
FastAPI + React op Debian 12
```

Productie-instellingen:

```dotenv
PUBLIC_BASE_URL=https://keuringen.intern.example
WEBAUTHN_RP_ID=keuringen.intern.example
WEBAUTHN_ORIGIN=https://keuringen.intern.example
```

De reverse proxy moet correcte `X-Forwarded-Proto`, `X-Forwarded-Host` en `X-Forwarded-For` headers doorgeven.

## 24. Automatisch starten na reboot

```bash
sudo systemctl is-enabled docker
sudo reboot
```

Na reboot:

```bash
cd /opt/keuringen/app
docker compose ps
curl --fail http://127.0.0.1:8080/health
```

## 25. Logging

```bash
cd /opt/keuringen/app
docker compose logs -f --tail=200
```

Voorbeeld `/etc/docker/daemon.json`:

```json
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "20m",
    "max-file": "5"
  }
}
```

Herstart Docker tijdens een onderhoudsvenster:

```bash
sudo systemctl restart docker
```

Log nooit wachtwoorden, tokens, WebAuthn-challenges, TOTP-geheimen, recovery codes of private sleutels.

## 26. Beveiligingshardening

Minimale maatregelen:

- alleen SSH-sleutels gebruiken;
- rootlogin via SSH uitschakelen;
- poort 8080 beperken tot interne bronnen;
- geen Redis- of databasepoort publiceren;
- secrets buiten Git bewaren;
- containerimages vastleggen op versies;
- containers als niet-root uitvoeren;
- Linux capabilities beperken;
- read-only filesystems gebruiken waar mogelijk;
- centrale logging en alerting activeren;
- periodieke kwetsbaarheidsscans uitvoeren.

Automatische beveiligingsupdates:

```bash
sudo apt install -y unattended-upgrades apt-listchanges
sudo dpkg-reconfigure --priority=low unattended-upgrades
```

## 27. Updateprocedure

Maak eerst een databaseback-up, controleer de NAS-back-up en noteer de huidige commit.

```bash
cd /opt/keuringen/app
git rev-parse HEAD
git fetch origin
git checkout main
git pull --ff-only origin main
docker compose config
docker compose build --pull
docker compose up -d
```

Controleer daarna zowel backend als frontend:

```bash
docker compose ps
curl --fail http://127.0.0.1:8080/health
curl -I http://127.0.0.1:8080/
```

## 28. Rollbackprocedure

Omdat React en FastAPI samen in één image zitten, wordt altijd de volledige webrelease teruggedraaid.

```bash
cd /opt/keuringen/app
git checkout <VORIGE-COMMIT-SHA>
docker compose build
docker compose up -d
```

Databaseherstel wordt alleen uitgevoerd volgens een vooraf getest herstelplan.

## 29. Problemen oplossen

### Poort 8080 is niet bereikbaar

```bash
sudo ss -lntp | grep 8080
sudo ufw status numbered
docker compose ps
docker compose logs --tail=200 web
```

### Poort 8080 is al in gebruik

```bash
sudo ss -lntp | grep ':8080'
sudo lsof -iTCP:8080 -sTCP:LISTEN
```

### React-route geeft 404

Controleer dat:

- de React-build aanwezig is in `frontend-dist`;
- de catch-all route na de API-routes is geregistreerd;
- de route naar `index.html` terugvalt;
- `/api`, `/events` en `/health` niet door de fallback worden onderschept.

### Frontend is leeg of assets geven 404

Controleer:

- het ingestelde Vite- of React-basepad;
- de map `/frontend-dist/assets` in de image;
- browserconsole en netwerkverzoeken;
- of de container opnieuw is gebouwd na frontendwijzigingen.

### NAS-mount ontbreekt

```bash
findmnt /mnt/keuringen-documents
sudo mount -a
journalctl -u remote-fs.target --no-pager
```

### WebAuthn of Passkeys werken niet

Controleer HTTPS, origin, RP ID, DNS, certificaat, proxyheaders en systeemtijd.

## 30. Opleverchecklist

- [ ] Debian 12 bijgewerkt
- [ ] Vast IP-adres en DNS ingesteld
- [ ] Tijdzone en NTP correct
- [ ] SSH beperkt tot beheerzone
- [ ] Docker Engine en Compose geïnstalleerd
- [ ] Repository op `main` uitgecheckt
- [ ] Geen Django geïnstalleerd
- [ ] Geen verplichte Nginx-hostservice geïnstalleerd
- [ ] Geen afzonderlijke frontendcontainer aanwezig
- [ ] React-build zit in dezelfde image als FastAPI
- [ ] FastAPI biedt `/`, assets en client-side routes aan
- [ ] FastAPI biedt API-, SSE- en healthroutes aan
- [ ] Webcontainer luistert op `0.0.0.0:8080`
- [ ] Docker publiceert `8080:8080`
- [ ] Redis uitsluitend intern bereikbaar
- [ ] PostgreSQL bereikbaar
- [ ] NAS-opslag correct gemount
- [ ] AI Gateway bereikbaar
- [ ] UFW en Proxmox-firewall ingesteld
- [ ] Health en React-routes getest
- [ ] Automatische start na reboot getest
- [ ] Logging en logrotatie actief
- [ ] Back-up en volledige release-rollback getest
- [ ] HTTPS-pad ingericht
- [ ] WebAuthn/Passkeys via definitieve HTTPS-URL getest

## 31. Samenvatting

De webrelease bestaat uit één applicatie-image:

```text
FastAPI + React-build
```

Django wordt niet gebruikt. Nginx is niet verplicht op de applicatie-VM. Er is geen afzonderlijke frontendcontainer.

De webcontainer biedt alle webfuncties aan via:

```text
0.0.0.0:8080
```

Docker Compose publiceert:

```yaml
ports:
  - "8080:8080"
```

Voor productie verzorgt een centrale reverse proxy of load balancer HTTPS en stuurt intern door naar de Debian 12 VM op poort 8080.