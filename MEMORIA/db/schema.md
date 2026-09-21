# Schema / Modelo de dados

## Tabelas

### providers
Catálogo de provedores (muda pouco).

| campo | tipo | notas |
|---|---|---|
| id | PK int | |
| slug | text UNIQUE | para URLs e testes |
| name | text | |
| website | text | |
| active | bool default true | controla presença na API pública |
| notes | text null | condições especiais |

### verifications
Uma ronda de verificação (o "quando" e "de onde").

| campo | tipo | notas |
|---|---|---|
| id | PK int | |
| provider_id | FK providers.id | |
| verified_at | timestamptz | hora da verificação |
| source_url | text | URL do provedor consultado |
| notes | text null | promoções, método usado |
| created_at | timestamptz | inserção na BD |

### quote_points
Pontos observados de cada ronda (o "quanto chega"). **`received_cve` é a fonte de verdade**; os restantes campos económicos são informativos/nulos.

| campo | tipo | notas |
|---|---|---|
| id | PK int | |
| verification_id | FK verifications.id | |
| amount_eur | NUMERIC(12,2) > 0 | UNIQUE (verification_id, amount_eur) |
| received_cve | NUMERIC(14,2) > 0 | fonte de verdade |
| fee_eur | NUMERIC(12,2) null | informativo |
| pct_fee | NUMERIC(8,4) null | informativo |
| fx_rate | NUMERIC(14,6) null | informativo |
| payment_method | text null | método de pagamento usado |
| payout_method | text null | método de recebimento |
| delivery_time | text null | tempo estimado/observado |

## Regras de derivação (não armazenadas)

- `effective_rate = received_cve / amount_eur`
- paridade oficial: constante `110.265` CVE por EUR (no código, com testes)
- `margin_pct = (1 - effective_rate / paridade) * 100`
- `cost_eur = amount_eur - received_cve / paridade`
- staleness: `now - verified_at > STALE_AFTER_DAYS` (constante, 7 dias por defeito)

## Montantes de referência (constante)

`[100, 250, 500, 1000, 2000]` EUR. Interpolação linear entre vizinhos; fora do intervalo faz-se clamp e `estimated=true`. Valor exato num ponto de referência -> `estimated=false`.

## Ronda atual

A ronda atual de um provedor é a `verification` com maior `id` (inserção sequencial).
O histórico preserva todas as rondas anteriores.