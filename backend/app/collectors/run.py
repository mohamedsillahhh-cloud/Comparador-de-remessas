"""Runner da recolha automática de cotações.

Faz a recolha e envia as rondas para a API admin (X-Admin-Token). Nunca inventa
dados: se um provedor falhar, não é registada ronda; se os valores forem iguais
à última ronda, a ronda é omitida.

Uso:
    python -m app.collectors.run --api https://api.example.com --token <ADMIN_TOKEN>
    python -m app.collectors.run --api http://localhost:8000 --token dev-admin-token --providers wise
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone

import httpx

from app.collectors.base import Collector, CollectorError
from app.collectors.wise import WiseCollector

COLLECTORS: dict[str, Collector] = {c.slug: c for c in (WiseCollector(),)}


def _request(
    http: httpx.Client, method: str, api: str, path: str, *, token: str, json=None
) -> list | None:
    response = http.request(
        method,
        f"{api.rstrip('/')}{path}",
        headers={"X-Admin-Token": token},
        json=json,
    )
    response.raise_for_status()
    return response.json()


def _latest_points(
    http: httpx.Client, api: str, provider_id: int, token: str
) -> set[tuple[float, float]] | None:
    data = _request(
        http,
        "GET",
        api,
        f"/api/admin/verifications?provider_id={provider_id}&limit=1",
        token=token,
    )
    if not data:
        return None
    latest = data[0]
    return {(float(p["amount_eur"]), float(p["received_cve"])) for p in latest["points"]}


def _point_payload(point) -> dict:
    return {
        "amount_eur": float(point.amount_eur),
        "received_cve": float(point.received_cve),
        "fee_eur": float(point.fee_eur) if point.fee_eur is not None else None,
        "pct_fee": float(point.pct_fee) if point.pct_fee is not None else None,
        "fx_rate": float(point.fx_rate) if point.fx_rate is not None else None,
        "payment_method": point.payment_method,
        "payout_method": point.payout_method,
        "delivery_time": point.delivery_time,
    }


def collect_rounds(
    providers: list[str],
    api: str,
    token: str,
    http: httpx.Client | None = None,
    collectors: dict[str, Collector] | None = None,
) -> int:
    own_http = http is None
    collector_map = collectors if collectors is not None else COLLECTORS
    created = 0
    unchanged = 0

    try:
        session = http or httpx.Client(timeout=30)
        try:
            registered = _request(
                session, "GET", api, "/api/admin/providers", token=token
            )
        except httpx.HTTPError as exc:
            print(f"[falha] API inacessível ou autenticação falhou: {exc}")
            return 1
        by_slug = {p["slug"]: p for p in registered}

        for slug in providers:
            collector = collector_map.get(slug)
            provider = by_slug.get(slug)
            if collector is None:
                print(f"[skip] sem collector implementado: {slug}")
                continue
            if provider is None:
                print(f"[skip] provedor não registado na API: {slug}")
                continue

            try:
                result = collector.collect()
            except CollectorError as exc:
                print(f"[falha] {slug}: {exc}")
                continue
            except Exception as exc:
                print(f"[falha] {slug}: recolha devolveu algo inesperado "
                      f"({exc.__class__.__name__}: {exc}); sem dados registados")
                continue
            if not result.points:
                print(f"[falha] {slug}: recolha devolveu zero pontos")
                continue

            current = {(float(p.amount_eur), float(p.received_cve)) for p in result.points}
            if _latest_points(session, api, provider["id"], token) == current:
                print(f"[sem alterações] {slug}")
                unchanged += 1
                continue

            payload = {
                "provider_id": provider["id"],
                "source": "auto",
                "verified_at": datetime.now(timezone.utc).isoformat(),
                "source_url": result.source_url,
                "notes": result.notes,
                "points": [_point_payload(p) for p in result.points],
            }
            try:
                _request(
                    session, "POST", api, "/api/admin/verifications", token=token, json=payload
                )
            except httpx.HTTPError as exc:
                print(f"[falha] {slug}: ao registar ronda: {exc}")
                continue
            print(f"[ok] {slug}: nova ronda com {len(result.points)} montantes")
            created += 1

        print(f"Resumo: {created} nova(s), {unchanged} sem alterações.")
        return 0 if (created or unchanged) else 1
    finally:
        if own_http:
            session.close()


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Recolhe cotações automáticas")
    parser.add_argument("--api", required=True, help="URL base da API (ex.: https://api.example.com)")
    parser.add_argument("--token", required=True, help="ADMIN_TOKEN da API")
    parser.add_argument(
        "--providers",
        default=",".join(COLLECTORS),
        help="Provedores a recolher (separados por vírgula)",
    )
    args = parser.parse_args(argv)
    providers = [slug.strip() for slug in args.providers.split(",") if slug.strip()]
    code = collect_rounds(providers, args.api, args.token)
    sys.exit(code)


if __name__ == "__main__":
    main()