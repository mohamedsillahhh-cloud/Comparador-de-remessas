export interface Provider {
  id: number;
  slug: string;
  name: string;
  website: string;
  active: boolean;
  notes: string | null;
}

export interface Meta {
  parity_cve_per_eur: number;
  stale_after_days: number;
  reference_amounts: number[];
}

export interface Quote {
  provider_id: number;
  provider_slug: string;
  provider_name: string;
  provider_website: string;
  amount_eur: number;
  received_cve: number;
  effective_rate: number;
  parity_rate: number;
  margin_pct: number;
  cost_eur: number;
  fee_eur: number | null;
  pct_fee: number | null;
  fx_rate: number | null;
  payment_method: string | null;
  payout_method: string | null;
  delivery_time: string | null;
  verified_at: string;
  source_url: string;
  source: string;
  estimated: boolean;
  stale: boolean;
}

export interface QuotePoint {
  amount_eur: number;
  received_cve: number;
  fee_eur: number | null;
  pct_fee: number | null;
  fx_rate: number | null;
  payment_method: string | null;
  payout_method: string | null;
  delivery_time: string | null;
}

export interface Verification {
  id: number;
  provider_id: number;
  verified_at: string;
  source_url: string;
  source: string;
  notes: string | null;
  created_at: string;
  points: QuotePoint[];
}

export interface VerificationInput {
  provider_id: number;
  source_url: string;
  source?: "manual" | "auto";
  notes?: string | null;
  points: {
    amount_eur: number;
    received_cve: number;
    fee_eur?: number | null;
    fx_rate?: number | null;
    payment_method?: string | null;
    payout_method?: string | null;
    delivery_time?: string | null;
  }[];
}