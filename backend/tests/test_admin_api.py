def auth() -> dict:
    return {"X-Admin-Token": "test-admin-token"}


def test_admin_requires_token(client):
    body = {"slug": "x", "name": "X", "website": "https://x.com"}
    assert client.post("/api/admin/providers", json=body).status_code == 401
    assert client.post("/api/admin/providers", json=body, headers={"X-Admin-Token": "wrong"}).status_code == 401
    assert client.get("/api/admin/verifications").status_code == 401


def test_create_provider(client):
    resp = client.post(
        "/api/admin/providers",
        json={"slug": "novo", "name": "Novo", "website": "https://novo.com"},
        headers=auth(),
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["slug"] == "novo"
    assert body["active"] is True


def test_create_provider_duplicate_slug(client):
    resp = client.post(
        "/api/admin/providers",
        json={"slug": "wise", "name": "Wise 2", "website": "https://x.com"},
        headers=auth(),
    )
    assert resp.status_code == 409


def test_create_provider_invalid_slug(client):
    resp = client.post(
        "/api/admin/providers",
        json={"slug": "Bad Slug!", "name": "X", "website": "https://x.com"},
        headers=auth(),
    )
    assert resp.status_code == 422


def test_deactivate_provider_hides_from_public(client):
    resp = client.patch("/api/admin/providers/1", json={"active": False}, headers=auth())
    assert resp.status_code == 200
    assert resp.json()["active"] is False
    provider_slugs = {p["slug"] for p in client.get("/api/providers").json()}
    assert "wise" not in provider_slugs


def test_admin_lists_all_providers_including_inactive(client):
    client.patch("/api/admin/providers/1", json={"active": False}, headers=auth())
    all_slugs = {p["slug"] for p in client.get("/api/admin/providers", headers=auth()).json()}
    assert "wise" in all_slugs
    public_slugs = {p["slug"] for p in client.get("/api/providers").json()}
    assert "wise" not in public_slugs


def test_patch_unknown_provider_404(client):
    assert client.patch("/api/admin/providers/999", json={"active": True}, headers=auth()).status_code == 404


def test_create_verification_batch(client):
    payload = {
        "provider_id": 1,
        "source_url": "https://example.com",
        "notes": "cartão de débito",
        "points": [
            {"amount_eur": 100, "received_cve": 11000, "fee_eur": 2.5, "fx_rate": 110.0},
            {"amount_eur": 250, "received_cve": 27500},
        ],
    }
    resp = client.post("/api/admin/verifications", json=payload, headers=auth())
    assert resp.status_code == 201
    body = resp.json()
    assert len(body["points"]) == 2
    assert body["source_url"] == "https://example.com"
    assert body["points"][0]["fee_eur"] == 2.5


def test_create_verification_default_source_manual(client):
    payload = {
        "provider_id": 1,
        "source_url": "https://example.com",
        "points": [{"amount_eur": 100, "received_cve": 11000}],
    }
    body = client.post("/api/admin/verifications", json=payload, headers=auth()).json()
    assert body["source"] == "manual"


def test_create_verification_auto_source(client):
    payload = {
        "provider_id": 1,
        "source_url": "https://wise.com/send",
        "source": "auto",
        "points": [{"amount_eur": 100, "received_cve": 11000}],
    }
    body = client.post("/api/admin/verifications", json=payload, headers=auth()).json()
    assert body["source"] == "auto"


def test_create_verification_invalid_source(client):
    payload = {
        "provider_id": 1,
        "source_url": "https://example.com",
        "source": "robot",
        "points": [{"amount_eur": 100, "received_cve": 11000}],
    }
    assert client.post("/api/admin/verifications", json=payload, headers=auth()).status_code == 422


def test_create_verification_duplicate_amount_conflict(client):
    payload = {
        "provider_id": 1,
        "source_url": "https://example.com",
        "points": [
            {"amount_eur": 100, "received_cve": 11000},
            {"amount_eur": 100, "received_cve": 11500},
        ],
    }
    assert client.post("/api/admin/verifications", json=payload, headers=auth()).status_code == 409


def test_create_verification_unknown_provider(client):
    payload = {
        "provider_id": 999,
        "source_url": "https://example.com",
        "points": [{"amount_eur": 100, "received_cve": 11000}],
    }
    assert client.post("/api/admin/verifications", json=payload, headers=auth()).status_code == 404


def test_create_verification_validation(client):
    payload = {
        "provider_id": 1,
        "source_url": "https://example.com",
        "points": [{"amount_eur": -5, "received_cve": 0}],
    }
    assert client.post("/api/admin/verifications", json=payload, headers=auth()).status_code == 422


def test_verification_history_preserved(client):
    for _ in range(2):
        client.post(
            "/api/admin/verifications",
            json={
                "provider_id": 1,
                "source_url": "https://example.com",
                "points": [{"amount_eur": 100, "received_cve": 11000}],
            },
            headers=auth(),
        )
    history = client.get("/api/admin/verifications", params={"provider_id": 1}, headers=auth()).json()
    assert len(history) == 2
    assert history[0]["id"] > history[1]["id"]  # mais recente primeiro


def test_latest_round_wins(client):
    for received in (11000, 11500):
        client.post(
            "/api/admin/verifications",
            json={
                "provider_id": 1,
                "source_url": "https://example.com",
                "points": [{"amount_eur": 100, "received_cve": received}],
            },
            headers=auth(),
        )
    quotes = client.get("/api/quotes", params={"amount_eur": 100}).json()
    assert quotes[0]["received_cve"] == 11500