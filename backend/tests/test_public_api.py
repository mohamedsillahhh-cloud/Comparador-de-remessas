from decimal import Decimal

from app.seed import PROVIDERS


def test_healthz(client):
    assert client.get("/api/healthz").json() == {"status": "ok"}


def test_meta(client):
    data = client.get("/api/meta").json()
    assert data["parity_cve_per_eur"] == 110.265
    assert data["stale_after_days"] == 7
    assert data["reference_amounts"] == [100, 250, 500, 1000, 2000]


def test_providers_seeded_active(client):
    data = client.get("/api/providers").json()
    assert {p["slug"] for p in data} == {p["slug"] for p in PROVIDERS}
    assert all(p["active"] for p in data)


def test_quotes_empty_without_verifications(client):
    assert client.get("/api/quotes", params={"amount_eur": 100}).json() == []


def test_quotes_require_amount(client):
    assert client.get("/api/quotes").status_code == 422
    assert client.get("/api/quotes", params={"amount_eur": 0}).status_code == 422


def test_quotes_sorted_by_received(client):
    headers = {"X-Admin-Token": "test-admin-token"}
    round_1 = {
        "provider_id": 2,
        "source_url": "https://example.com",
        "points": [
            {"amount_eur": 100, "received_cve": 11000},
            {"amount_eur": 250, "received_cve": 27500},
        ],
    }
    round_2 = {
        "provider_id": 1,
        "source_url": "https://example.com",
        "points": [
            {"amount_eur": 100, "received_cve": 11050},
            {"amount_eur": 250, "received_cve": 27625},
        ],
    }
    assert client.post("/api/admin/verifications", json=round_1, headers=headers).status_code == 201
    assert client.post("/api/admin/verifications", json=round_2, headers=headers).status_code == 201

    quotes = client.get("/api/quotes", params={"amount_eur": 100}).json()
    assert [q["provider_id"] for q in quotes] == [1, 2]
    assert all(q["estimated"] is False for q in quotes)
    assert quotes[0]["received_cve"] > quotes[1]["received_cve"]


def test_quotes_estimated_outside_range(client):
    headers = {"X-Admin-Token": "test-admin-token"}
    payload = {
        "provider_id": 1,
        "source_url": "https://example.com",
        "points": [{"amount_eur": 100, "received_cve": 11000}],
    }
    client.post("/api/admin/verifications", json=payload, headers=headers)
    quotes = client.get("/api/quotes", params={"amount_eur": 50}).json()
    assert len(quotes) == 1
    assert quotes[0]["estimated"] is True


def test_inactive_provider_not_in_quotes(client):
    headers = {"X-Admin-Token": "test-admin-token"}
    payload = {
        "provider_id": 1,
        "source_url": "https://example.com",
        "points": [{"amount_eur": 100, "received_cve": 11000}],
    }
    client.post("/api/admin/verifications", json=payload, headers=headers)
    client.patch("/api/admin/providers/1", json={"active": False}, headers=headers)
    assert client.get("/api/quotes", params={"amount_eur": 100}).json() == []