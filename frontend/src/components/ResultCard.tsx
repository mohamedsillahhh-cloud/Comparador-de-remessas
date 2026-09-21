import { formatCve, formatDateTime, formatEur, formatPct, formatRate } from "../format";
import type { Quote } from "../types";

interface Props {
  quote: Quote;
  rank: number;
}

function Row({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="row">
      <span className="row-label">{label}</span>
      <span className="row-value">{children}</span>
    </div>
  );
}

export default function ResultCard({ quote, rank }: Props) {
  const fee = quote.fee_eur != null ? formatEur(quote.fee_eur) : "não indicada";
  const fx = quote.fx_rate != null ? formatRate(quote.fx_rate) : "não indicada";

  return (
    <article className="card">
      <div className="card-head">
        <span className="rank">{rank}</span>
        <div>
          <h3>{quote.provider_name}</h3>
          <a href={quote.provider_website} target="_blank" rel="noreferrer">
            {quote.provider_website}
          </a>
        </div>
        <div className="received">
          <strong>{formatCve(quote.received_cve)}</strong>
          <span>recebidos</span>
        </div>
      </div>

      <div className="badges">
        <span className="badge">1 € = {formatRate(quote.effective_rate)} CVE</span>
        <span className={quote.margin_pct > 0 ? "badge warn" : "badge ok"}>
          {quote.margin_pct > 0
            ? `${formatPct(quote.margin_pct)} abaixo da paridade`
            : "na paridade oficial"}
        </span>
        {quote.estimated && <span className="badge warn">estimativa (fora da malha verificada)</span>}
        {quote.source === "auto" && <span className="badge">recolha automática</span>}
        {quote.stale && <span className="badge danger">desatualizado</span>}
      </div>

      <details>
        <summary>Detalhes</summary>
        <div className="details">
          <Row label="Envia">{formatEur(quote.amount_eur)}</Row>
          <Row label="Comissão">{fee}</Row>
          <Row label="Câmbio aplicado">{fx}</Row>
          <Row label="Paridade oficial">1 € = {formatRate(quote.parity_rate)} CVE</Row>
          <Row label="Custo cambial">{formatEur(quote.cost_eur)}</Row>
          <Row label="Pagamento">{quote.payment_method ?? "não indicado"}</Row>
          <Row label="Recebimento">{quote.payout_method ?? "não indicado"}</Row>
          <Row label="Entrega">{quote.delivery_time ?? "não indicado"}</Row>
          <Row label="Verificado em">{formatDateTime(quote.verified_at)}</Row>
          <Row label="Fonte">
            <a href={quote.source_url} target="_blank" rel="noreferrer">
              {quote.source_url}
            </a>
          </Row>
        </div>
      </details>
    </article>
  );
}