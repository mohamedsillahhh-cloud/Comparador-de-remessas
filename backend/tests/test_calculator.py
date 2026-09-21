from datetime import datetime, timezone
from decimal import Decimal

import pytest

from app.models import Provider, QuotePoint, Verification
from app.services.calculator import build_quote, interpolate


def make_round(points):
    provider = Provider(id=1, slug="p", name="P", website="https://example.com")
    verification = Verification(
        provider=provider,
        verified_at=datetime.now(timezone.utc),
        source_url="https://example.com",
        source="manual",
    )
    for amount, received in points:
        verification.points.append(
            QuotePoint(amount_eur=Decimal(amount), received_cve=Decimal(received))
        )
    return provider, verification


def test_interpolate_exact_match():
    provider, verification = make_round([(Decimal("100"), Decimal("11026.50")), (Decimal("250"), Decimal("27566.25"))])
    quote = build_quote(provider, verification, Decimal("100"))
    assert quote.received_cve == 11026.50
    assert quote.estimated is False
    assert quote.effective_rate == 110.265


def test_interpolate_between_points():
    provider, verification = make_round([(Decimal("100"), Decimal("11026.50")), (Decimal("250"), Decimal("27566.25"))])
    quote = build_quote(provider, verification, Decimal("175"))
    assert quote.received_cve == 19296.375
    assert quote.estimated is False


def test_clamp_below_min():
    provider, verification = make_round([(Decimal("100"), Decimal("11026.50")), (Decimal("250"), Decimal("27566.25"))])
    quote = build_quote(provider, verification, Decimal("50"))
    assert quote.received_cve == 11026.50
    assert quote.estimated is True


def test_clamp_above_max():
    provider, verification = make_round([(Decimal("100"), Decimal("11026.50")), (Decimal("250"), Decimal("27566.25"))])
    quote = build_quote(provider, verification, Decimal("3000"))
    assert quote.received_cve == 27566.25
    assert quote.estimated is True


def test_single_point_clamp():
    provider, verification = make_round([(Decimal("500"), Decimal("55132.50"))])
    quote = build_quote(provider, verification, Decimal("500"))
    assert quote.received_cve == 55132.50
    assert quote.estimated is False
    quote2 = build_quote(provider, verification, Decimal("501"))
    assert quote2.received_cve == 55132.50
    assert quote2.estimated is True


def test_direction_between_points_is_directional():
    points = [QuotePoint(amount_eur=Decimal("100"), received_cve=Decimal("11000")),
              QuotePoint(amount_eur=Decimal("200"), received_cve=Decimal("22000"))]
    received, estimated, _ = interpolate(Decimal("150"), points)
    assert received == Decimal("16500")
    assert estimated is False


def test_derived_indicators_parity():
    provider, verification = make_round([(Decimal("100"), Decimal("11026.50"))])
    quote = build_quote(provider, verification, Decimal("100"))
    assert quote.parity_rate == 110.265
    assert quote.margin_pct == 0.0
    assert quote.cost_eur == 0.0


def test_derived_indicators_margin():
    provider, verification = make_round([(Decimal("100"), Decimal("9900.00"))])
    quote = build_quote(provider, verification, Decimal("100"))
    assert quote.margin_pct == pytest.approx(10.2163, abs=0.0001)
    assert quote.cost_eur == pytest.approx(10.2163, abs=0.0001)