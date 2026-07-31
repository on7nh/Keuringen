-- Required PostgreSQL extensions, per docs/03_Database_Ontwerp.md section 3.
-- `vector` is intentionally left out until pgvector is confirmed for production.
CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS citext;
CREATE EXTENSION IF NOT EXISTS pg_trgm;
