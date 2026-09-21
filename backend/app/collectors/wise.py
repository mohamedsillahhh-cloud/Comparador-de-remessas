"""Collector da Wise.

Usa a API pública de cotações da Wise (POST /quotes, sem autenticação) — o mesmo
endpoint que alimenta o simulador público. Regista o método padrão de pagamento
"transferência bancária" (payIn=BANK_TRANSFER). O valor recebido é calculado a
partir dos campos devolvidos: (montante - comissão) * taxa.
"""

from decimal import Decimal, InvalidOperation

import httpx

from app.collectors.base import Collector, CollectorError, CollectorResult, PointData
from app.config import REFERENCE_AMOUNTS

DEFAULT_BASE_URL = "https://api.wise.com/2026Q3"
WISE_SOURCE_URL = (
    "https://wise.com/send#/enterAmount?sourceCurrency=EUR&targetCurrency=CVE"
)
USER_AGENT = "comparador-remessas/0.1 (+open-source)"

PAYIN_LABELS = {
    "BANK_TRANSFER": "transferência bancária",
    "DEBIT": "cartão de débito",
    "CARD": "cartão de débito",
    "APPLE_PAY": "Apple Pay",
    "SODEXO": "Sodexo",
    "IDEAL": "iDEAL",
}


def _to_decimal(value: object) -> Decimal | None:
    if value is None:
        return None
    try:
        return Decimal(str(value))
    except (ValueError, InvalidOperation):
        return None


def _payment_option(data: dict) -> dict | None:
    options = data.get("paymentOptions") or []
    active = [option for option in options if not option.get("disabled")]
    if not active:
        return None
    for option in active:
        if option.get("payIn") == "BANK_TRANSFER":
            return option
    return active[0]


def _point_from_quote(data: object, amount_eur: Decimal) -> PointData | None:
    if not isinstance(data, dict):
        return None
    rate = _to_decimal(data.get("rate"))
    if rate is None or rate <= 0:
        return None
    option = _payment_option(data)
    if option is None:
        return None
    total = (option.get("price") or {}).get("total") or {}
    fee = _to_decimal((total.get("value") or {}).get("amount"))
    if fee is None or fee < 0:
        return None
    received = (amount_eur - fee) * rate
    if received <= 0:
        return None
    pay_in = option.get("payIn")
    return PointData(
        amount_eur=amount_eur,
        received_cve=received.quantize(Decimal("0.01")),
        fee_eur=fee,
        pct_fee=(fee / amount_eur * 100).quantize(Decimal("0.0001")),
        fx_rate=rate,
        payment_method=PAYIN_LABELS.get(pay_in, pay_in),
        payout_method="conta bancária",
        delivery_time=option.get("formattedEstimatedDelivery"),
    )


class WiseCollector(Collector):
    slug = "wise"
    name = "Wise"

    def __init__(self, base_url: str = DEFAULT_BASE_URL, client: httpx.Client | None = None):
        self._base_url = base_url
        self._client = client

    def collect(self) -> CollectorResult:
        close_client = self._client is None
        client = self._client or httpx.Client(
            timeout=20, headers={"User-Agent": USER_AGENT}
        )
        try:
            points: list[PointData] = []
            for amount in REFERENCE_AMOUNTS:
                try:
                    response = client.post(
                        f"{self._base_url}/quotes",
                        json={
                            "sourceCurrency": "EUR",
                            "targetCurrency": "CVE",
                            "sourceAmount": float(amount),
                        },
                    )
                    response.raise_for_status()
                    point = _point_from_quote(response.json(), Decimal(amount))
                except (httpx.HTTPError, ValueError, TypeError):
                    point = None
                if point is not None:
                    points.append(point)
        finally:
            if close_client:
                client.close()

        if not points:
            raise CollectorError("Wise: nenhuma cotação válida obtida")

        return CollectorResult(
            provider_slug=self.slug,
            source_url=WISE_SOURCE_URL,
            notes=(
                "Recolha automática via API pública de cotações da Wise "
                "(POST /quotes, sem autenticação). Método padrão: transferência "
                "bancária (SWIFT)."
            ),
            points=points,
        )