from datetime import datetime, timedelta, timezone
from decimal import Decimal

from app.config import PARITY_CVE_PER_EUR, get_settings
from app.models import Provider, QuotePoint, Verification
from app.schemas import QuoteOut


def _f(value: Decimal | None) -> float | None:
    return float(value) if value is not None else None


def _as_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def interpolate(amount_eur: Decimal, points: list[QuotePoint]) -> tuple[Decimal, bool, QuotePoint]:
    """Devolve (received_cve, estimated, ponto mais próximo p/ informação)."""
    ordered = sorted(points, key=lambda p: p.amount_eur)
    closest = min(ordered, key=lambda p: abs(p.amount_eur - amount_eur))
    first, last = ordered[0], ordered[-1]

    if amount_eur == first.amount_eur or amount_eur == last.amount_eur:
        exact = next(p for p in ordered if p.amount_eur == amount_eur)
        return exact.received_cve, False, exact
    if amount_eur < first.amount_eur or amount_eur > last.amount_eur:
        return closest.received_cve, True, closest

    for low, high in zip(ordered, ordered[1:]):
        if low.amount_eur <= amount_eur <= high.amount_eur:
            ratio = (amount_eur - low.amount_eur) / (high.amount_eur - low.amount_eur)
            received = low.received_cve + (high.received_cve - low.received_cve) * ratio
            return received, False, closest

    raise AssertionError("unreachable")


def build_quote(provider: Provider, verification: Verification, amount_eur: Decimal) -> QuoteOut:
    received, estimated, point = interpolate(amount_eur, verification.points)

    effective_rate = received / amount_eur
    parity = PARITY_CVE_PER_EUR
    margin_pct = (1 - effective_rate / parity) * 100
    cost_eur = amount_eur - received / parity

    stale = _as_utc(datetime.now(timezone.utc)) - _as_utc(verification.verified_at) > timedelta(
        days=get_settings().stale_after_days
    )

    return QuoteOut(
        provider_id=provider.id,
        provider_slug=provider.slug,
        provider_name=provider.name,
        provider_website=provider.website,
        amount_eur=float(amount_eur),
        received_cve=float(received),
        effective_rate=float(effective_rate),
        parity_rate=float(parity),
        margin_pct=float(margin_pct),
        cost_eur=float(cost_eur),
        fee_eur=_f(point.fee_eur),
        pct_fee=_f(point.pct_fee),
        fx_rate=_f(point.fx_rate),
        payment_method=point.payment_method,
        payout_method=point.payout_method,
        delivery_time=point.delivery_time,
        verified_at=verification.verified_at,
        source_url=verification.source_url,
        source=verification.source,
        estimated=estimated,
        stale=stale,
    )