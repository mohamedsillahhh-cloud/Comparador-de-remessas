# Decisões de design aprovadas

Decisões registadas e aprovadas pelo dono do produto. Não alterar sem razão técnica
concreta discutida primeiro.

- **Stack:** FastAPI + PostgreSQL + React/Vite. Deploy Render (backend + BD) e Vercel (frontend).
- **Fonte de verdade da cotação:** valor recebido (`received_cve`). Comissão/taxa/câmbio são
  informativos e podem ser nulos.
- **Histórico:** rondas de verificação em `verifications` + `quote_points` (append-only).
- **Admin:** token único `ADMIN_TOKEN` via header `X-Admin-Token` nos endpoints de escrita.
  Sem contas de utilizador no MVP.
- **Seed inicial:** Wise, Remitly, WorldRemit, Ria, Western Union, MoneyGram.
- **Malha de referência:** 100, 250, 500, 1000, 2000 EUR.
- **Cálculo para valor arbitrário:** interpolação linear entre pontos vizinhos; fora do
  intervalo -> clamp + `estimated=true`; valor exato -> `estimated=false`.
- **Staleness:** após 7 dias (constante no código), exposto em `GET /api/meta`.
- **UI:** pt-PT; `Intl.NumberFormat`; EUR com 2 casas, CVE sem casas; CSS puro (sem Tailwind).
- **Docs:** README.md + runbook de verificação manual (docs/verificacao-manual.md).
- **Testes:** pytest (back-end), Vitest + Testing Library (front-end). BD de teste: SQLite.
- **Coleção híbrida:** recolha pode ser automática (`source="auto"` via `backend/app/collectors/`)
  ou manual (`source="manual"`, predefinido). Os collectors usam apenas fontes públicas, sem
  login, e **nunca inventam dados**: montante que falhe é omitido; round só é criada se pelo
  menos um montante for válido; valores iguais à última round são omitidos. Um runner CLI
  (`python -m app.collectors.run`) envia as rondas para a API admin; o GitHub Actions corre-o
  diariamente (secrets `QUOTES_API_URL` e `ADMIN_TOKEN`). Wise: coletado automaticamente via
  API pública de cotações (POST /quotes, sem auth). Remitly e restantes: apenas manuais por agora
  (os seus simuladores não expõem dados sem login/anti-bot).
- **Automação fora do MVP:** scraping completo de todos os provedores, APIs complexas, contas de
  utilizador, multi-corredor, mobile, submissão comunitária de rondas (fase futura).