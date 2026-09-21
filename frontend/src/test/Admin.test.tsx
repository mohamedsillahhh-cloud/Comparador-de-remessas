import { render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import Admin from "../pages/Admin";

const meta = {
  parity_cve_per_eur: 110.265,
  stale_after_days: 7,
  reference_amounts: [100, 250, 500, 1000, 2000],
};

const providers = [
  { id: 1, slug: "wise", name: "Wise", website: "https://wise.com", active: true, notes: null },
  { id: 2, slug: "remitly", name: "Remitly", website: "https://remitly.com", active: false, notes: null },
];

function jsonResponse(data: unknown) {
  return new Response(JSON.stringify(data), {
    status: 200,
    headers: { "Content-Type": "application/json" },
  });
}

describe("Admin", () => {
  beforeEach(() => {
    localStorage.clear();
    vi.restoreAllMocks();
    vi.stubGlobal(
      "fetch",
      vi.fn(async (url: string) => {
        if (String(url).includes("/api/meta")) return jsonResponse(meta);
        if (String(url).includes("/api/admin/providers")) return jsonResponse(providers);
        throw new Error(`pedido inesperado: ${url}`);
      }),
    );
  });

  it("pede o token quando não existe sessão", () => {
    render(<Admin />);
    expect(screen.getByLabelText("Token")).toBeInTheDocument();
  });

  it("lista provedores ativos e inativos quando há token", async () => {
    localStorage.setItem("admin_token", "test-token");
    render(<Admin />);
    expect((await screen.findAllByText("Wise")).length).toBeGreaterThan(0);
    expect(screen.getAllByText("Remitly").length).toBeGreaterThan(0);
    expect(screen.getByText("Desativar")).toBeInTheDocument();
    expect(screen.getByText("Ativar")).toBeInTheDocument();
  });
});