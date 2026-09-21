# Arquitetura

## Visão geral

Monorepo com backend FastAPI + PostgreSQL e frontend React (Vite) + TypeScript.
Deploy: backend e PostgreSQL no Render; frontend na Vercel.

## Estrutura

```
backend/     FastAPI, SQLAlchemy 2, Alembic, Pydantic v2
frontend/    React + Vite + TypeScript (calculadora + admin)
scripts/     check-memoria.sh (+ check-memoria.ps1 equivalente)
docker-compose.yml   Postgres + backend de dev
MEMORIA/     memória do projeto
docs/        runbook de verificação manual
```

## Backend

- App síncrono (não async), SQLAlchemy 2 com sessões por request.
- Sem camada repository: router -> serviço de cálculo -> modelo.
- Migrações com Alembic; seed de providers no arranque (idempotente por slug).
- Autenticação de escrita: token único `ADMIN_TOKEN` via header `X-Admin-Token`.
- CORS limitado às origens em `CORS_ORIGINS`.

## Frontend

- Duas páginas com routing por hash (`/` e `#/admin`), sem react-router.
- Fetch nativo (sem react-query).
- CSS único simples (sem Tailwind).
- Formatação pt-PT com Intl.NumberFormat.

## Deploy

- Render: Web Service (Dockerfile), PostgreSQL gerido; migrações no arranque (`alembic upgrade head`).
- Vercel: build Vite padrão, `VITE_API_URL` aponta para o backend Render.
- Env vars: `DATABASE_URL`, `ADMIN_TOKEN`, `CORS_ORIGINS`.

## Recolha automática (collectors)

- `backend/app/collectors/`: módulo por provedor (base + wise). `Collector.collect() -> CollectorResult`
  (montantes + URL fonte + notas). Base de dados de `verifications.source` = `manual|auto`.
- Guardas: montante inválido é omitido; sem montantes válidos -> `CollectorError` (round não criada);
  round iguais à última são ignoradas (dedup). Opções de pagamento `disabled` da Wise são ignoradas;
  payload não-dict (ex.: resposta vinda como lista) é ignorado e indica `CollectorError`.
- Runner: `python -m app.collectors.run --api <URL> --token <ADMIN_TOKEN> [--providers wise]` — resolve
  providers, compara com a última round e faz POST em `POST /api/admin/verifications` com `source="auto"`.
  Exit 0 se houve nova round ou sem alterações; 1 se tudo falhou. Falhas de API/auth são reportadas de
  forma limpa (exit 1); erros inesperados por provedor são registados como `[falha]` sem interromper o
  processo nem inventar dados.
- Wise: `POST https://api.wise.com/2026Q3/quotes` (sem auth). A fórmula `(montante - comissão) * taxa`
  foi validada contra o campo `targetAmount` da própria API (iguais nos 5 montantes de referência).
  Método padrão `BANK_TRANSFER` (SWIFT), com fallback para a primeira opção ativa. Remitly e restantes:
  manuais (simuladores sem acesso público).
- CI: `.github/workflows/collect-quotes.yml` — cron diário 05:15 UTC, secrets `QUOTES_API_URL` + `ADMIN_TOKEN`
  (pode disparar manualmente com `workflow_dispatch`).
- Frontend produção: `VITE_API_URL` obrigatória (sem fallback para localhost em prod); aviso de arranque
  quando `ADMIN_TOKEN` é o default de dev.

## Como correr (dev)

- `docker compose up db` -> Postgres local (exposto na porta 5433 do host; a 5432 é ocupada
  por um PostgreSQL nativo do Windows instalado na máquina).
- Backend: Python 3.12 local, precisa de `backend/.env` com `DATABASE_URL`
  (`postgresql+psycopg://comparador:comparador@localhost:5433/comparador`), depois
  `alembic upgrade head` e `uvicorn app.main:app --reload` (em backend/); alternativa
  `docker compose up backend`.
- Frontend: em frontend/, `npm install`, `npm run dev` (porta 5173).
- Testes backend: `pytest` em backend/.
- Testes frontend: `npm test` em frontend/.
- Memória: `scripts/check-memoria.ps1` (ou `.sh` via bash/Git).