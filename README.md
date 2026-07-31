# Digitaal Keurings- en Documentbeheer

Centraal platform voor technische documenten, keuringsverslagen en
risicoanalyses. Volledige functionele en technische specificaties staan in
[`docs/`](docs/).

## Architectuur

- **Backend**: Python, FastAPI, SQLAlchemy, Alembic, PostgreSQL
- **Frontend**: React, TypeScript, Vite — gebouwd en meegeleverd in dezelfde
  container als de backend (geen aparte frontendcontainer, geen Nginx)
- **Achtergrondtaken**: Celery + Redis (worker en scheduler)
- **Bestandsopslag**: lokale/NAS-gekoppelde directory, aangestuurd door de
  centrale `NamingService`

Zie [`docs/20_Installatie_Website.md`](docs/20_Installatie_Website.md) voor de
volledige installatieprocedure op een Debian 12 VM, en
[`PROGRESS.md`](PROGRESS.md) voor wat op dit moment is geïmplementeerd.

## Snel starten (lokale ontwikkeling)

```bash
cp .env.example .env
# pas JWT_SECRET, TOTP_ENCRYPTION_KEY en wachtwoorden aan

docker compose up -d --build
# docker-compose.override.yml voegt automatisch een lokale PostgreSQL-container toe

docker compose exec web alembic upgrade head
docker compose exec web env SEED_ADMIN_EMAIL=admin@example.org SEED_ADMIN_PASSWORD=change-me \
  python -m app.seed
```

De applicatie is bereikbaar op <http://localhost:8080>. De seed-uitvoer toont
een TOTP-secret voor de eerste beheerder — voeg deze toe aan een
authenticator-app vóór de eerste aanmelding.

## Backend zonder Docker (ontwikkeling)

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp ../.env.example .env   # en pas aan voor een lokale PostgreSQL-instantie
alembic upgrade head
python -m app.seed
uvicorn app.main:app --reload --port 8080
```

## Frontend apart draaien (hot reload tijdens ontwikkeling)

```bash
cd frontend
npm install
npm run dev
```

Vite proxieert `/api` naar `http://127.0.0.1:8080` (zie `vite.config.ts`) —
start de backend apart voor lokale frontendontwikkeling met hot reload. Voor
een productie-achtige test bouwt `npm run build` de app naar `frontend/dist`,
die vervolgens (via de Docker-build) als statische bestanden door FastAPI
wordt aangeboden.

## Migraties

```bash
cd backend
alembic revision --autogenerate -m "omschrijving"
alembic upgrade head
```

## Testen uitgevoerd tijdens ontwikkeling

- Volledige Alembic-migratiecyclus (upgrade / downgrade / upgrade) tegen een
  echte PostgreSQL-instantie, zonder schema drift (`alembic check`)
- End-to-end API-test: aanmelden (wachtwoord + TOTP), organisatie/Site
  aanmaken, document uploaden (bestandsnaamconventie geverifieerd op schijf),
  keuring bevestigen (automatische vervaldatumberekening en planning)
- Browsertest (Playwright): aanmelden, navigatie tussen Dashboard, Sites,
  Documenten en Keuringen
