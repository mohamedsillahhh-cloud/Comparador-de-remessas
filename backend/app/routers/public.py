from decimal import Decimal

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.config import PARITY_CVE_PER_EUR, REFERENCE_AMOUNTS, get_settings
from app.db import get_session
from app.models import Provider, Verification
from app.schemas import ProviderOut, QuoteOut
from app.services.calculator import build_quote

router = APIRouter(prefix="/api", tags=["public"])


@router.get("/healthz")
def healthz() -> dict:
    return {"status": "ok"}


@router.get("/providers")
def list_providers(session: Session = Depends(get_session)) -> list[ProviderOut]:
    providers = session.scalars(
        select(Provider).where(Provider.active).order_by(Provider.name)
    ).all()
    return list(providers)


@router.get("/meta")
def meta() -> dict:
    settings = get_settings()
    return {
        "parity_cve_per_eur": float(PARITY_CVE_PER_EUR),
        "stale_after_days": settings.stale_after_days,
        "reference_amounts": list(REFERENCE_AMOUNTS),
    }


def _latest_verification(session: Session, provider_id: int) -> Verification | None:
    latest_id = session.scalar(
        select(Verification.id)
        .where(Verification.provider_id == provider_id)
        .order_by(Verification.id.desc())
        .limit(1)
    )
    if latest_id is None:
        return None
    return session.scalar(
        select(Verification)
        .options(selectinload(Verification.points))
        .where(Verification.id == latest_id)
    )


@router.get("/quotes")
def get_quotes(
    amount_eur: float = Query(gt=0, le=1_000_000),
    session: Session = Depends(get_session),
) -> list[QuoteOut]:
    providers = session.scalars(select(Provider).where(Provider.active)).all()
    quotes: list[QuoteOut] = []
    for provider in providers:
        verification = _latest_verification(session, provider.id)
        if verification is None:
            continue
        quotes.append(build_quote(provider, verification, Decimal(amount_eur)))
    quotes.sort(key=lambda q: q.received_cve, reverse=True)
    return quotes