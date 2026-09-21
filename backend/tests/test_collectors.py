from decimal import Decimal
import json

import httpx
import pytest

from app.collectors import run as collector_run
from app.collectors.base import CollectorError
from app.collectors.wise import WiseCollector, _point_from_quote


def quote_payload(amount: float, rate: float = 110.5, fee: float | None = 10.0) -> dict:
    price = {"type": "TOTAL", "value": {"amount": fee, "currency": "EUR"}}
    return {
        "sourceAmount": amount,
        "rate": rate,
        "paymentOptions": [
            {
                "payIn": "BANK_TRANSFER",
                "payOut": "SWIFT",
                "feePercentage": None if fee is None else fee / amount,
                "price": {"total": price},
                "formattedEstimatedDelivery": "by Monday, September 28",
            }
        ],
    }


def test_point_ok():
    point = _point_from_quote(quote_payload(100, 110.5, 10), Decimal("100"))
    assert point is not None
    assert point.received_cve == Decimal("9945.00")
    assert point.fee_eur == Decimal("10.00")
    assert point.fx_rate == Decimal("110.5")
    assert point.payment_method == "transferência bancária"
    assert point.payout_method == "conta bancária"


def test_point_skips_when_fee_missing():
    assert _point_from_quote(quote_payload(100, 110.5, None), Decimal("100")) is None


def test_point_skips_when_rate_missing():
    payload = quote_payload(100, fee=10)
    payload["rate"] = None
    assert _point_from_quote(payload, Decimal("100")) is None


def test_point_skips_when_no_payment_options():
    payload = quote_payload(100, fee=10)
    payload["paymentOptions"] = []
    assert _point_from_quote(payload, Decimal("100")) is None


def test_point_skips_when_received_negative():
    payload = quote_payload(100, rate=1.0, fee=200)
    assert _point_from_quote(payload, Decimal("100")) is None


def _collector(handler):
    client = httpx.Client(transport=httpx.MockTransport(handler))
    return WiseCollector(client=client)


def _wise_handler():
    def handler(request: httpx.Request) -> httpx.Response:
        amount = json.loads(request.content)["sourceAmount"]
        return httpx.Response(200, json=quote_payload(amount))

    return handler


def test_collector_builds_five_points():
    result = _collector(_wise_handler()).collect()
    assert len(result.points) == 5
    assert result.provider_slug == "wise"
    assert result.source_url.startswith("https://wise.com")
    amounts = sorted(float(p.amount_eur) for p in result.points)
    assert amounts == [100, 250, 500, 1000, 2000]
    for point in result.points:
        assert point.received_cve > 0
        assert point.fx_rate == Decimal("110.5")


def test_collector_raises_when_api_fails():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(500, text="erro")

    with pytest.raises(CollectorError):
        _collector(handler).collect()


def _api_handler(verifications, posted):
    def handler(request: httpx.Request) -> httpx.Response:
        path = request.url.path
        if request.method == "GET" and path == "/api/admin/providers":
            return httpx.Response(
                200,
                json=[{"id": 11, "slug": "wise", "name": "Wise", "website": "https://wise.com", "active": True, "notes": None}],
            )
        if request.method == "GET" and path == "/api/admin/verifications":
            return httpx.Response(200, json=verifications)
        if request.method == "POST" and path == "/api/admin/verifications":
            body = json.loads(request.content)
            posted.append(body)
            return httpx.Response(201, json=body)
        if request.method == "POST" and path.endswith("/quotes"):
            amount = json.loads(request.content)["sourceAmount"]
            return httpx.Response(200, json=quote_payload(amount))
        return httpx.Response(404, text="não encaminhado")

    return handler


def test_run_posts_new_round():
    posted: list[dict] = []
    client = httpx.Client(transport=httpx.MockTransport(_api_handler([], posted)))
    code = collector_run.collect_rounds(
        ["wise"], "http://api.example", "secret", http=client, collectors={"wise": WiseCollector(client=client)}
    )
    assert code == 0
    assert len(posted) == 1
    body = posted[0]
    assert body["provider_id"] == 11
    assert body["source"] == "auto"
    assert len(body["points"]) == 5
    assert all(p["received_cve"] > 0 for p in body["points"])


def test_run_skips_when_unchanged():
    collector = _collector(_wise_handler())
    result = collector.collect()
    latest = [
        {
            "provider_id": 11,
            "points": [
                {"amount_eur": float(p.amount_eur), "received_cve": float(p.received_cve)}
                for p in result.points
            ],
        }
    ]
    posted: list[dict] = []
    client = httpx.Client(transport=httpx.MockTransport(_api_handler(latest, posted)))
    code = collector_run.collect_rounds(
        ["wise"], "http://api.example", "secret", http=client, collectors={"wise": WiseCollector(client=client)}
    )
    assert code == 0
    assert posted == []


def test_run_fails_when_collector_fails():
    def handler(request: httpx.Request) -> httpx.Response:
        if request.method == "GET" and request.url.path == "/api/admin/providers":
            return httpx.Response(200, json=[{"id": 11, "slug": "wise", "name": "Wise", "website": "x", "active": True, "notes": None}])
        if request.method == "GET" and request.url.path == "/api/admin/verifications":
            return httpx.Response(200, json=[])
        if request.method == "POST" and request.url.path.endswith("/quotes"):
            return httpx.Response(500, text="erro")
        return httpx.Response(404, text="não encaminhado")

    posted: list[dict] = []
    client = httpx.Client(transport=httpx.MockTransport(handler))
    code = collector_run.collect_rounds(
        ["wise"], "http://api.example", "secret", http=client, collectors={"wise": WiseCollector(client=client)}
    )
    assert code == 1
    assert posted == []


def test_point_skips_disabled_option():
    payload = quote_payload(100, rate=110.5, fee=10)
    payload["paymentOptions"][0]["disabled"] = True
    assert _point_from_quote(payload, Decimal("100")) is None


def test_point_prefers_active_bank_transfer_over_disabled():
    payload = {
        "sourceAmount": 100,
        "rate": 110.5,
        "paymentOptions": [
            {
                "payIn": "BANK_TRANSFER",
                "disabled": True,
                "price": {"total": {"value": {"amount": 5, "currency": "EUR"}}},
            },
            {
                "payIn": "DEBIT",
                "disabled": False,
                "price": {"total": {"value": {"amount": 10, "currency": "EUR"}}},
            },
        ],
    }
    point = _point_from_quote(payload, Decimal("100"))
    assert point is not None
    assert point.payment_method == "cartão de débito"
    assert point.fee_eur == Decimal("10.00")


def test_point_skips_when_response_not_dict():
    assert _point_from_quote(["não esperado"], Decimal("100")) is None


def _failing_collector():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, text="não é JSON")
    return _collector(handler)


def test_collector_raises_on_invalid_json_everywhere():
    with pytest.raises(CollectorError):
        _failing_collector().collect()


def test_collector_raises_on_http_404():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(404, text="missing")

    with pytest.raises(CollectorError):
        _collector(handler).collect()


def test_collector_raises_on_timeout():
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectTimeout("falhou a ligar", request=request)

    with pytest.raises(CollectorError):
        _collector(handler).collect()


def test_collector_returns_partial_round_without_fabricating():
    def handler(request: httpx.Request) -> httpx.Response:
        amount = json.loads(request.content)["sourceAmount"]
        if amount in (250, 500):
            return httpx.Response(500, text="erro momentâneo")
        return httpx.Response(200, json=quote_payload(amount))

    result = _collector(handler).collect()
    assert sorted(float(p.amount_eur) for p in result.points) == [100, 1000, 2000]
    assert all(p.received_cve > 0 for p in result.points)


def test_run_posts_partial_round():
    def handler(request: httpx.Request) -> httpx.Response:
        path = request.url.path
        if request.method == "GET" and path == "/api/admin/providers":
            return httpx.Response(200, json=[{"id": 11, "slug": "wise", "name": "W", "website": "x", "active": True, "notes": None}])
        if request.method == "GET" and path == "/api/admin/verifications":
            return httpx.Response(200, json=[])
        if request.method == "POST" and path == "/api/admin/verifications":
            posted.append(json.loads(request.content))
            return httpx.Response(201, json=posted[-1])
        if request.method == "POST" and path.endswith("/quotes"):
            amount = json.loads(request.content)["sourceAmount"]
            if amount in (250, 500):
                return httpx.Response(500, text="erro")
            return httpx.Response(200, json=quote_payload(amount))
        return httpx.Response(404, text="não encaminhado")

    posted: list[dict] = []
    client = httpx.Client(transport=httpx.MockTransport(handler))
    code = collector_run.collect_rounds(
        ["wise"], "http://api.example", "secret", http=client, collectors={"wise": WiseCollector(client=client)}
    )
    assert code == 0
    assert len(posted) == 1
    assert sorted(p["amount_eur"] for p in posted[0]["points"]) == [100, 1000, 2000]


def test_run_returns_1_when_api_auth_fails():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(401, json={"detail": "Admin token inválido"})

    client = httpx.Client(transport=httpx.MockTransport(handler))
    code = collector_run.collect_rounds(
        ["wise"], "http://api.example", "secreto", http=client, collectors={"wise": WiseCollector(client=client)}
    )
    assert code == 1


def test_run_does_not_crash_on_unexpected_payload():
    def handler(request: httpx.Request) -> httpx.Response:
        path = request.url.path
        if request.method == "GET" and path == "/api/admin/providers":
            return httpx.Response(200, json=[{"id": 11, "slug": "wise", "name": "W", "website": "x", "active": True, "notes": None}])
        if request.method == "GET" and path == "/api/admin/verifications":
            return httpx.Response(200, json=[])
        if request.method == "POST" and path.endswith("/quotes"):
            return httpx.Response(200, json=["payload", "inesperado"])
        return httpx.Response(404, text="não encaminhado")

    client = httpx.Client(transport=httpx.MockTransport(handler))
    code = collector_run.collect_rounds(
        ["wise"], "http://api.example", "secret", http=client, collectors={"wise": WiseCollector(client=client)}
    )
    assert code == 1