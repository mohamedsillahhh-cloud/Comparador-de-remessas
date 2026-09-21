import { render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import Calculator from "../pages/Calculator";

const meta = {
  parity_cve_per_eur: 110.265,
  stale_after_days: 7,
  reference_amounts: [100, 250, 500, 1000, 2000],
};

const quote = {
  provider_id: 1,
  provider_slug: "wise",
  provider_name: "Wise",
  provider_website: "https://wise.com",
  amount_eur: 100,
  received_cve: 10900.5,
  effective_rate: 109.005,
  parity_rate: 110.265,
  margin_pct: 1.14,
  cost_eur: 1.14,
  fee_eur: 0.7,
  pct_fee: null,
  fx_rate: 110.1,
  payment_method: "cartão de débito",
  payout_method: "conta bancária",
  delivery_time: "1-2 dias",
  verified_at: "2026-09-21T12:00:00Z",
  source_url: "https://wise.com",
  source: "auto",
  estimated: false,
  stale: false,
};

function jsonResponse(data: unknown) {
  return new Response(JSON.stringify(data), {
    status: 200,
    headers: { "Content-Type": "application/json" },
  });
}

function mockFetch(quotes: unknown[]) {
  vi.stubGlobal(
    "fetch",
    vi.fn(async (url: string) => {
      if (String(url).includes("/api/meta")) return jsonResponse(meta);
      if (String(url).includes("/api/quotes")) return jsonResponse(quotes);
      throw new Error(`pedido inesperado: ${url}`);
    }),
  );
}

describe("Calculator", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it("mostra os provedores recebidos da API", async () => {
    mockFetch([quote]);
    render(<Calculator />);
    expect(await screen.findByText("Wise")).toBeInTheDocument();
    expect(screen.getByText("recebidos")).toBeInTheDocument();
    expect(screen.getAllByText(/Paridade oficial/).length).toBeGreaterThan(0);
    expect(screen.getByText("recolha automática")).toBeInTheDocument();
  });

  it("mostra estado vazio quando não há cotações", async () => {
    mockFetch([]);
    render(<Calculator />);
    expect(await screen.findByText(/Ainda não há cotações verificadas/)).toBeInTheDocument();
  });

  it("mostra erro quando a API falha", async () => {
    vi.stubGlobal("fetch", vi.fn(async () => new Response("erro", { status: 500 })));
    render(<Calculator />);
    expect(await screen.findByText(/Não foi possível obter cotações/)).toBeInTheDocument();
  });
});