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
- [x] Fase 9 - Revisão de produção: hardening de collectors e runner (guardas), segurança, deploy-ready.

## Estado atual

- MVP completo e verificado. Backend e frontend implementados, testados e documentados.
- Fase 8 (coleção híbrida): recolha automática da Wise via API pública (sem auth); runner CLI
  `python -m app.collectors.run`; cron GitHub Actions; `verifications.source` (`manual|auto`).
- Fase 9 (revisão produção): collectors ignoram opções `disabled` da Wise e payloads não-dict;
  runner falha de forma limpa em API/auth e recupera por provedor de erros inesperados (nunca
  inventa dados); frontend em produção exige `VITE_API_URL` (falha cedo em vez de apontar para
  localhost); aviso no arranque se `ADMIN_TOKEN` for o default de dev.

## Verificações

- `pytest` no backend: 52 testes a passar (SQLite); cobrem collectors (timeout, 4xx/5xx, JSON
  inválido, campos ausentes, `disabled`, zero quotes, rondas parciais, dedup, auth falha) e `source`.
- `npm test` no frontend: 5 testes a passar; `npm run build` (tsc + vite) OK; 0 vulnerabilidades.
- Migrações (0001 + 0002, head único) aplicadas em Postgres real via Docker; API validada end-to-end.
- Fórmula Wise validada ao vivo: `(montante - comissão) * taxa` == `targetAmount` da API em todos
  os 5 montantes (diff 0,00). Rondas automáticas reais na BD dev (ids 2, 3, 4, `source="auto"`).
- E2E local: healthz OK, admin 401 sem/errado token e 200 com token, runner criou ronda, calculator
  interpola (175 EUR) e faz clamp com `estimated=true` (50 / 3000 EUR), sem `stale`.

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