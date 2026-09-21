import { useEffect, useState } from "react";
import { getMeta, getQuotes } from "../api";
import ResultCard from "../components/ResultCard";
import { formatRate } from "../format";
import type { Meta, Quote } from "../types";

const DEFAULT_AMOUNT = "100";

export default function Calculator() {
  const [amountText, setAmountText] = useState(DEFAULT_AMOUNT);
  const [quotes, setQuotes] = useState<Quote[]>([]);
  const [meta, setMeta] = useState<Meta | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const amount = Number(amountText);
  const validAmount = Number.isFinite(amount) && amount > 0;

  useEffect(() => {
    getMeta()
      .then(setMeta)
      .catch(() => setMeta(null));
  }, []);

  useEffect(() => {
    if (!validAmount) {
      setQuotes([]);
      return;
    }
    let active = true;
    setLoading(true);
    setError(null);
    getQuotes(amount)
      .then((data) => {
        if (active) setQuotes(data);
      })
      .catch((e: Error) => {
        if (active) setError(e.message);
      })
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => {
      active = false;
    };
  }, [amount, validAmount]);

  return (
    <section className="page">
      <h1>Quanto chega a Cabo Verde?</h1>
      <p className="subtitle">
        Escolhe o valor a enviar de Portugal e vê quanto o destinatário recebe em escudos, por provedor.
      </p>

      <div className="calculator">
        <label htmlFor="amount">Valor a enviar</label>
        <div className="amount-input">
          <input
            id="amount"
            type="number"
            min="1"
            step="10"
            value={amountText}
            onChange={(e) => setAmountText(e.target.value)}
          />
          <span>EUR</span>
        </div>
        {meta && (
          <p className="meta">
            Paridade oficial: 1 € = {formatRate(meta.parity_cve_per_eur)} CVE · aviso de desatualização após{" "}
            {meta.stale_after_days} dias
          </p>
        )}
      </div>

      {!validAmount && <p className="notice">Introduz um valor maior que zero.</p>}
      {error && <p className="notice danger">Não foi possível obter cotações: {error}</p>}
      {loading && <p className="notice">A calcular…</p>}

      {validAmount && !loading && !error && quotes.length === 0 && (
        <p className="notice">Ainda não há cotações verificadas para mostrar.</p>
      )}

      <div className="results">
        {quotes.map((quote, index) => (
          <ResultCard key={quote.provider_id} quote={quote} rank={index + 1} />
        ))}
      </div>
    </section>
  );
}