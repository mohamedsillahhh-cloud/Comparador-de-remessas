import type { Meta, Provider, Quote, Verification, VerificationInput } from "./types";

const BASE = (import.meta.env.VITE_API_URL as string | undefined) ?? "http://localhost:8000";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${BASE}${path}`, init);
  if (!response.ok) {
    let detail = `Erro ${response.status}`;
    try {
      const body = await response.json();
      if (body?.detail) {
        detail = typeof body.detail === "string" ? body.detail : JSON.stringify(body.detail);
      }
    } catch {
      // resposta sem corpo JSON: mantém a mensagem genérica
    }
    throw new Error(detail);
  }
  return (await response.json()) as T;
}

export const getMeta = () => request<Meta>("/api/meta");
export const getQuotes = (amount: number) => request<Quote[]>(`/api/quotes?amount_eur=${amount}`);

const adminHeaders = (token: string) => ({
  "X-Admin-Token": token,
  "Content-Type": "application/json",
});

export const adminGetProviders = (token: string) =>
  request<Provider[]>("/api/admin/providers", { headers: adminHeaders(token) });

export const adminCreateProvider = (
  token: string,
  payload: { slug: string; name: string; website: string; notes?: string },
) =>
  request<Provider>("/api/admin/providers", {
    method: "POST",
    headers: adminHeaders(token),
    body: JSON.stringify(payload),
  });

export const adminUpdateProvider = (token: string, id: number, payload: { active?: boolean }) =>
  request<Provider>(`/api/admin/providers/${id}`, {
    method: "PATCH",
    headers: adminHeaders(token),
    body: JSON.stringify(payload),
  });

export const adminCreateVerification = (token: string, payload: VerificationInput) =>
  request<Verification>("/api/admin/verifications", {
    method: "POST",
    headers: adminHeaders(token),
    body: JSON.stringify(payload),
  });

export const adminGetVerifications = (token: string, providerId?: number) =>
  request<Verification[]>(
    `/api/admin/verifications${providerId ? `?provider_id=${providerId}` : ""}`,
    { headers: adminHeaders(token) },
  );