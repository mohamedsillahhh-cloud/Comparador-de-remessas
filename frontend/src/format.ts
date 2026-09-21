const eur = new Intl.NumberFormat("pt-PT", { style: "currency", currency: "EUR" });
const cve = new Intl.NumberFormat("pt-PT", { maximumFractionDigits: 0 });
const rate = new Intl.NumberFormat("pt-PT", { maximumFractionDigits: 4 });
const pct = new Intl.NumberFormat("pt-PT", { maximumFractionDigits: 2 });
const dateTime = new Intl.DateTimeFormat("pt-PT", { dateStyle: "medium", timeStyle: "short" });

export const formatEur = (value: number) => eur.format(value);
export const formatCve = (value: number) => `${cve.format(value)} CVE`;
export const formatRate = (value: number) => rate.format(value);
export const formatPct = (value: number) => `${pct.format(value)} %`;
export const formatDateTime = (iso: string) => dateTime.format(new Date(iso));