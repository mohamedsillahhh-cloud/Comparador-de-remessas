import { useCallback, useEffect, useState } from "react";
import {
  adminCreateProvider,
  adminCreateVerification,
  adminGetProviders,
  adminGetVerifications,
  adminUpdateProvider,
  getMeta,
} from "../api";
import { formatCve, formatDateTime, formatEur } from "../format";
import type { Provider, Verification } from "../types";

const TOKEN_KEY = "admin_token";
const FALLBACK_AMOUNTS = [100, 250, 500, 1000, 2000];

interface PointDraft {
  received: string;
  fee: string;
  fx: string;
}

const emptyDraft = (amounts: number[]): Record<number, PointDraft> =>
  Object.fromEntries(amounts.map((a) => [a, { received: "", fee: "", fx: "" }]));

export default function Admin() {
  const [token, setToken] = useState(() => localStorage.getItem(TOKEN_KEY) ?? "");
  const [tokenInput, setTokenInput] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [providers, setProviders] = useState<Provider[]>([]);
  const [amounts, setAmounts] = useState<number[]>(FALLBACK_AMOUNTS);

  const [newProvider, setNewProvider] = useState({ slug: "", name: "", website: "" });

  const [providerId, setProviderId] = useState<number | "">("");
  const [sourceUrl, setSourceUrl] = useState("");
  const [notes, setNotes] = useState("");
  const [paymentMethod, setPaymentMethod] = useState("");
  const [payoutMethod, setPayoutMethod] = useState("");
  const [deliveryTime, setDeliveryTime] = useState("");
  const [draft, setDraft] = useState<Record<number, PointDraft>>(() => emptyDraft(FALLBACK_AMOUNTS));

  const [historyProvider, setHistoryProvider] = useState<number | "">("");
  const [history, setHistory] = useState<Verification[]>([]);

  const loadProviders = useCallback(
    async (currentToken: string) => {
      const data = await adminGetProviders(currentToken);
      setProviders(data);
    },
    [],
  );

  useEffect(() => {
    getMeta()
      .then((meta) => {
        setAmounts(meta.reference_amounts);
        setDraft(emptyDraft(meta.reference_amounts));
      })
      .catch(() => undefined);
  }, []);

  useEffect(() => {
    if (!token) return;
    setError(null);
    loadProviders(token).catch((e: Error) => setError(e.message));
  }, [token, loadProviders]);

  function saveToken() {
    localStorage.setItem(TOKEN_KEY, tokenInput);
    setToken(tokenInput);
    setTokenInput("");
  }

  function logout() {
    localStorage.removeItem(TOKEN_KEY);
    setToken("");
    setProviders([]);
    setHistory([]);
  }

  async function toggleProvider(provider: Provider) {
    try {
      await adminUpdateProvider(token, provider.id, { active: !provider.active });
      await loadProviders(token);
    } catch (e) {
      setError((e as Error).message);
    }
  }

  async function submitProvider(event: React.FormEvent) {
    event.preventDefault();
    try {
      await adminCreateProvider(token, newProvider);
      setNewProvider({ slug: "", name: "", website: "" });
      await loadProviders(token);
    } catch (e) {
      setError((e as Error).message);
    }
  }

  function updateDraft(amount: number, field: keyof PointDraft, value: string) {
    setDraft((prev) => ({ ...prev, [amount]: { ...prev[amount], [field]: value } }));
  }

  async function submitVerification(event: React.FormEvent) {
    event.preventDefault();
    if (providerId === "") {
      setError("Escolhe um provedor.");
      return;
    }
    const points = amounts
      .map((amount) => ({ amount, draft: draft[amount] }))
      .filter(({ draft: d }) => d.received.trim() !== "")
      .map(({ amount, draft: d }) => ({
        amount_eur: amount,
        received_cve: Number(d.received),
        fee_eur: d.fee.trim() === "" ? null : Number(d.fee),
        fx_rate: d.fx.trim() === "" ? null : Number(d.fx),
        payment_method: paymentMethod || null,
        payout_method: payoutMethod || null,
        delivery_time: deliveryTime || null,
      }));
    if (points.length === 0) {
      setError("Preenche pelo menos um valor recebido.");
      return;
    }
    try {
      await adminCreateVerification(token, {
        provider_id: providerId,
        source_url: sourceUrl,
        notes: notes || null,
        points,
      });
      setDraft(emptyDraft(amounts));
      setNotes("");
      setError(null);
      if (historyProvider === providerId) await loadHistory(providerId);
    } catch (e) {
      setError((e as Error).message);
    }
  }

  async function loadHistory(id: number | "") {
    setHistoryProvider(id);
    if (id === "") {
      setHistory([]);
      return;
    }
    try {
      setHistory(await adminGetVerifications(token, id));
    } catch (e) {
      setError((e as Error).message);
    }
  }

  if (!token) {
    return (
      <section className="page narrow">
        <h1>Admin</h1>
        <p className="subtitle">Introduz o token de administração para atualizar cotações.</p>
        <div className="calculator">
          <label htmlFor="token">Token</label>
          <div className="amount-input">
            <input
              id="token"
              type="password"
              value={tokenInput}
              onChange={(e) => setTokenInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && saveToken()}
            />
          </div>
          <button onClick={saveToken} disabled={!tokenInput}>
            Entrar
          </button>
        </div>
      </section>
    );
  }

  return (
    <section className="page">
      <div className="admin-head">
        <h1>Admin</h1>
        <button className="secondary" onClick={logout}>
          Sair
        </button>
      </div>

      {error && <p className="notice danger">{error}</p>}

      <h2>Provedores</h2>
      <ul className="provider-list">
        {providers.map((provider) => (
          <li key={provider.id}>
            <span className={provider.active ? "dot on" : "dot off"} />
            <strong>{provider.name}</strong>
            <span className="muted">{provider.slug}</span>
            <button className="secondary" onClick={() => toggleProvider(provider)}>
              {provider.active ? "Desativar" : "Ativar"}
            </button>
          </li>
        ))}
      </ul>

      <form className="inline-form" onSubmit={submitProvider}>
        <input
          placeholder="slug"
          value={newProvider.slug}
          onChange={(e) => setNewProvider({ ...newProvider, slug: e.target.value })}
        />
        <input
          placeholder="nome"
          value={newProvider.name}
          onChange={(e) => setNewProvider({ ...newProvider, name: e.target.value })}
        />
        <input
          placeholder="website"
          value={newProvider.website}
          onChange={(e) => setNewProvider({ ...newProvider, website: e.target.value })}
        />
        <button type="submit">Adicionar provedor</button>
      </form>

      <h2>Nova verificação</h2>
      <form className="verification-form" onSubmit={submitVerification}>
        <div className="grid-3">
          <label>
            Provedor
            <select value={providerId} onChange={(e) => setProviderId(Number(e.target.value))}>
              <option value="">— escolher —</option>
              {providers.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.name}
                </option>
              ))}
            </select>
          </label>
          <label>
            URL da fonte
            <input value={sourceUrl} onChange={(e) => setSourceUrl(e.target.value)} placeholder="https://..." />
          </label>
          <label>
            Notas
            <input value={notes} onChange={(e) => setNotes(e.target.value)} placeholder="promoção, método, etc." />
          </label>
        </div>

        <div className="grid-3">
          <label>
            Método de pagamento
            <input value={paymentMethod} onChange={(e) => setPaymentMethod(e.target.value)} placeholder="cartão de débito" />
          </label>
          <label>
            Método de recebimento
            <input value={payoutMethod} onChange={(e) => setPayoutMethod(e.target.value)} placeholder="conta bancária" />
          </label>
          <label>
            Entrega
            <input value={deliveryTime} onChange={(e) => setDeliveryTime(e.target.value)} placeholder="1-2 dias" />
          </label>
        </div>

        <table className="points">
          <thead>
            <tr>
              <th>Envio (EUR)</th>
              <th>Recebido (CVE) *</th>
              <th>Comissão (EUR)</th>
              <th>Câmbio</th>
            </tr>
          </thead>
          <tbody>
            {amounts.map((amount) => (
              <tr key={amount}>
                <td>{amount}</td>
                <td>
                  <input
                    type="number"
                    value={draft[amount]?.received ?? ""}
                    onChange={(e) => updateDraft(amount, "received", e.target.value)}
                  />
                </td>
                <td>
                  <input
                    type="number"
                    step="0.01"
                    value={draft[amount]?.fee ?? ""}
                    onChange={(e) => updateDraft(amount, "fee", e.target.value)}
                  />
                </td>
                <td>
                  <input
                    type="number"
                    step="0.001"
                    value={draft[amount]?.fx ?? ""}
                    onChange={(e) => updateDraft(amount, "fx", e.target.value)}
                  />
                </td>
              </tr>
            ))}
          </tbody>
        </table>

        <button type="submit">Guardar ronda</button>
      </form>

      <h2>Histórico</h2>
      <label className="history-select">
        Provedor
        <select value={historyProvider} onChange={(e) => loadHistory(e.target.value === "" ? "" : Number(e.target.value))}>
          <option value="">— escolher —</option>
          {providers.map((p) => (
            <option key={p.id} value={p.id}>
              {p.name}
            </option>
          ))}
        </select>
      </label>

{history.map((verification) => (
          <div key={verification.id} className="history-round">
            <div className="history-head">
              <strong>Ronda #{verification.id}</strong>
              <span>{formatDateTime(verification.verified_at)}</span>
              {verification.source === "auto" && <span className="badge">automático</span>}
              <a href={verification.source_url} target="_blank" rel="noreferrer">
                fonte
              </a>
            </div>
          {verification.notes && <p className="muted">{verification.notes}</p>}
          <table className="points">
            <thead>
              <tr>
                <th>Envio</th>
                <th>Recebido</th>
                <th>Comissão</th>
                <th>Câmbio</th>
              </tr>
            </thead>
            <tbody>
              {verification.points.map((point) => (
                <tr key={point.amount_eur}>
                  <td>{formatEur(point.amount_eur)}</td>
                  <td>{formatCve(point.received_cve)}</td>
                  <td>{point.fee_eur != null ? formatEur(point.fee_eur) : "—"}</td>
                  <td>{point.fx_rate != null ? point.fx_rate : "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ))}
    </section>
  );
}