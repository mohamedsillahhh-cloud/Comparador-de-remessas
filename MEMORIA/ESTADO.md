# Estado do Projeto

Comparador de remessas EUR -> CVE (Portugal -> Cabo Verde).

## Fases

- [x] Fase 0 - Bootstrap (scripts check-memoria, docker-compose, memória).
- [x] Fase 1 - Backend core.
- [x] Fase 2 - Admin API.
- [x] Fase 3 - Testes backend (29 testes).
- [x] Fase 4 - Frontend Calculadora.
- [x] Fase 5 - Frontend Admin.
- [x] Fase 6 - Deploy configs + testes frontend (5 testes).
- [x] Fase 7 - Runbook, memória final.
- [x] Fase 8 - Coleção híbrida: collectors (Wise) + runner CLI + GitHub Actions cron + `source` em rondas.

## Estado atual

- MVP completo e verificado. Backend e frontend implementados, testados e documentados.
- Fase 8 (coleção híbrida): recolha automática da Wise via API pública (sem auth); runner CLI
  `python -m app.collectors.run`; cron GitHub Actions; `verifications.source` (`manual|auto`).
- Endpoints públicos: `GET /api/healthz`, `/api/meta`, `/api/providers`, `/api/quotes?amount_eur=`.
- Admin (header `X-Admin-Token`): `GET/POST /api/admin/providers`,
  `PATCH /api/admin/providers/{id}`, `POST/GET /api/admin/verifications` (POST aceita `source`).
- Frontend: calculadora (`#/`) e admin (`#/admin`), routing por hash; tags "automático"/"recolha automática".
- Docs: `README.md`, `docs/verificacao-manual.md`.
- Deploy documentado no README (Render Dockerfile + Postgres; Vercel Vite).

## Verificações

- `pytest` no backend: 42 testes a passar (SQLite); inclui collectors (mock HTTP) e `source`.
- `npm test` no frontend: 5 testes a passar; `npm run build` (tsc + vite) OK; 0 vulnerabilidades.
- Migrações (0001 + 0002) aplicadas em Postgres real via Docker; API validada end-to-end.
- Collector Wise testado ao vivo: round real registada (id 2, `source="auto"`), 100 EUR -> 9 801,14 CVE
  (comissão 11,35 €, taxa 110,56).

## Ambiente de dev

- Docker Desktop (daemon) para Postgres e backend; `docker compose up db backend`.
- Python 3.12 e Node 24 locais; testes backend correm com `pytest` no venv local.
- Na máquina existe também um PostgreSQL nativo do Windows (`postgresql-x64-16`, serviço
  `Running`) que ocupa a porta 5432. Para evitar conflito, o Postgres do Docker é exposto
  na porta **5433** (`docker-compose.yml`). O `backend/.env` aponta
  `DATABASE_URL` para `localhost:5433` para correr o backend local (alembic/uvicorn).
- Limitação: no Windows local, o `psycopg[binary]` é bloqueado pela política de aplicações
  (nem sempre — depende da sessão e da cópia instalada); por isso o caminho robusto de dev
  é via Docker (`docker compose up db backend`). Testes usam SQLite.
- `scripts/check-memoria.sh` corre via Docker: `docker run --rm -v "${PWD}:/app" -w /app bash:5.2 bash scripts/check-memoria.sh`.

## Contactos/guia do projecto

- Ver MEMORIA/ARQUITETURA.md para estrutura e como correr.
- Ver MEMORIA/db/schema.md para o modelo de dados.
- Ver MEMORIA/decisoes/decisoes.md para decisões aprovadas.