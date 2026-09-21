# Comparador de Remessas EUR → CVE

Compara quanto **chega realmente** a Cabo Verde quando se envia dinheiro de Portugal.
Para cada provedor, a pergunta central é: *se enviar X €, quanto recebe o destinatário em CVE?*

O valor recebido (`received_cve`) é a fonte de verdade da cotação. Comissão, câmbio aplicado
e métodos são informação complementar, mostrada quando disponível.

## Stack

- **Backend:** FastAPI + PostgreSQL (SQLAlchemy 2, Alembic), Python 3.12.
- **Frontend:** React + Vite + TypeScript, CSS puro.
- **Deploy:** backend e PostgreSQL no Render; frontend na Vercel.

## Estrutura

```
backend/    API, modelos, migrações, testes (pytest)
frontend/   SPA: calculadora + admin, testes (Vitest)
scripts/    check-memoria.sh (+ check-memoria.ps1)
docs/       runbook de verificação manual
MEMORIA/    memória do projeto
```

## Como correr (dev)

### Backend + PostgreSQL (Docker)

```bash
docker compose up db backend
```

A API fica em `http://localhost:8000`. As migrações correm no arranque do backend.
A BD do Docker está exposta no host em `localhost:5433` (a 5432 é usada por um
PostgreSQL do Windows que também está instalado na máquina).

### Backend local (sem Docker para a app)

Requer um PostgreSQL acessível. Levanta só a BD:

```bash
docker compose up -d db
```

Cria `backend/.env` a partir de `backend/.env.example`, com
`DATABASE_URL=postgresql+psycopg://comparador:comparador@localhost:5433/comparador`.
Já existe um `backend/.env` com estes valores.

```bash
cd backend
python -m venv .venv
.venv/Scripts/pip install -e ".[dev]"   # Windows
.venv/Scripts/python -m alembic upgrade head
.venv/Scripts/python -m uvicorn app.main:app --reload
```

> Nota (Windows): se o driver `psycopg[binary]` for bloqueado por políticas de aplicação
> locais, usa `docker compose up db backend` e acede à API em `http://localhost:8000`.

### Frontend

```bash
cd frontend
npm install
npm run dev        # http://localhost:5173
```

Configura `VITE_API_URL` (por defeito `http://localhost:8000`) a partir de `frontend/.env.example`.

## Testes

```bash
# Backend (SQLite em memória)
cd backend
.venv/Scripts/python -m pytest

# Frontend
cd frontend
npm test
npm run build     # typecheck + build
```

## Endpoints

Públicos:

- `GET /api/healthz`
- `GET /api/meta` — paridade oficial, dias até aviso de desatualização, montantes de referência
- `GET /api/providers` — provedores ativos
- `GET /api/quotes?amount_eur=100` — cotações ordenadas por valor recebido

Admin (header `X-Admin-Token` obrigatório):

- `GET /api/admin/providers` — todos, incluindo inativos
- `POST /api/admin/providers`
- `PATCH /api/admin/providers/{id}` — ativar/desativar
- `POST /api/admin/verifications` — nova ronda (lote de montantes)
- `GET /api/admin/verifications?provider_id=` — histórico

## Modelo de cálculo

- Paridade oficial: **1 EUR = 110.265 CVE** (constante).
- Para um valor arbitrário: interpolação linear entre os montantes de referência
  (100, 250, 500, 1000, 2000 EUR). Fora do intervalo: clamp ao extremo com `estimated=true`.
- Indicadores derivados: taxa efetiva, diferença face à paridade, custo cambial em EUR.
- Aviso de desatualização após 7 dias (constante `STALE_AFTER_DAYS`).

## Deploy

### Render (backend + base de dados)

1. Cria um PostgreSQL no Render.
2. Cria um Web Service a partir de `backend/Dockerfile`.
3. Define as variáveis de ambiente:
   - `DATABASE_URL` (fornecida pelo Render Postgres, com driver `postgresql+psycopg://`)
   - `ADMIN_TOKEN` (segredo forte)
   - `CORS_ORIGINS` (domínio do frontend na Vercel)
4. O comando do contentor corre `alembic upgrade head` antes de arrancar a API.

### Vercel (frontend)

1. Root directory: `frontend`.
2. Build: `npm run build`; output: `dist`.
3. Variável de ambiente `VITE_API_URL` com o URL público do backend no Render.

## Administração de dados

As cotações podem ser **manuais** (verificadas no simulador oficial e registadas no admin —
ver `docs/verificacao-manual.md`) ou **automáticas** (`source="auto"`), recolhidas de fontes
públicas sem login.

### Recolha automática (Wise)

A Wise expõe a API pública de cotações usada pelo próprio simulador (sem autenticação), pelo que
a sua ronda é gerada automaticamente.

```bash
cd backend
python -m app.collectors.run --api http://localhost:8000 --token dev-admin-token --providers wise
```

O runner **nunca inventa dados**: só regista a ronda se obtiver montantes válidos e não os tiver
repetidos face à última ronda. Em CI, um workflow (`.github/workflows/collect-quotes.yml`) corre
isto diariamente (05:15 UTC) com os secrets `QUOTES_API_URL` e `ADMIN_TOKEN`; podes disparar
manualmente na aba Actions.

Remitly, WorldRemit, Ria, Western Union e MoneyGram não expõem cotações sem login/anti-bot:
continuam manuais, pelo runbook e pelo admin.

## Memória do projeto

Regras em `AGENT.md`. Validação:

```bash
# Windows (PowerShell)
powershell -File scripts/check-memoria.ps1

# ou via Docker
docker run --rm -v "$PWD:/app" -w /app bash:5.2 bash scripts/check-memoria.sh
```
