from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Header, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.config import get_settings
from app.db import get_session
from app.models import Provider, QuotePoint, Verification
from app.schemas import (
    PointOut,
    ProviderCreate,
    ProviderOut,
    ProviderUpdate,
    VerificationIn,
    VerificationOut,
)

router = APIRouter(prefix="/api/admin", tags=["admin"])


def require_admin(x_admin_token: str | None = Header(default=None)) -> None:
    token = get_settings().admin_token
    if not token or x_admin_token != token:
        raise HTTPException(status_code=401, detail="Admin token inválido")


def _point_out(point: QuotePoint) -> PointOut:
    return PointOut(
        amount_eur=float(point.amount_eur),
        received_cve=float(point.received_cve),
        fee_eur=float(point.fee_eur) if point.fee_eur is not None else None,
        pct_fee=float(point.pct_fee) if point.pct_fee is not None else None,
        fx_rate=float(point.fx_rate) if point.fx_rate is not None else None,
        payment_method=point.payment_method,
        payout_method=point.payout_method,
        delivery_time=point.delivery_time,
    )


def _verification_out(verification: Verification) -> VerificationOut:
    return VerificationOut(
        id=verification.id,
        provider_id=verification.provider_id,
        verified_at=verification.verified_at,
        source_url=verification.source_url,
        source=verification.source,
        notes=verification.notes,
        created_at=verification.created_at,
        points=[_point_out(p) for p in verification.points],
    )


@router.get("/providers", response_model=list[ProviderOut])
def list_all_providers(
    session: Session = Depends(get_session),
    _: None = Depends(require_admin),
) -> list[Provider]:
    return list(session.scalars(select(Provider).order_by(Provider.name)).all())


@router.post("/providers", response_model=ProviderOut, status_code=201)
def create_provider(
    payload: ProviderCreate,
    session: Session = Depends(get_session),
    _: None = Depends(require_admin),
) -> Provider:
    duplicate = session.scalar(select(Provider).where(Provider.slug == payload.slug))
    if duplicate:
        raise HTTPException(status_code=409, detail="slug já existe")
    provider = Provider(**payload.model_dump())
    session.add(provider)
    session.commit()
    session.refresh(provider)
    return provider


@router.patch("/providers/{provider_id}", response_model=ProviderOut)
def update_provider(
    provider_id: int,
    payload: ProviderUpdate,
    session: Session = Depends(get_session),
    _: None = Depends(require_admin),
) -> Provider:
    provider = session.get(Provider, provider_id)
    if provider is None:
        raise HTTPException(status_code=404, detail="provedor não existe")
    data = payload.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(provider, field, value)
    session.commit()
    session.refresh(provider)
    return provider


@router.post("/verifications", response_model=VerificationOut, status_code=201)
def create_verification(
    payload: VerificationIn,
    session: Session = Depends(get_session),
    _: None = Depends(require_admin),
) -> Verification:
    provider = session.get(Provider, payload.provider_id)
    if provider is None:
        raise HTTPException(status_code=404, detail="provedor não existe")

    verification = Verification(
        provider_id=payload.provider_id,
        verified_at=payload.verified_at or datetime.now(timezone.utc),
        source_url=payload.source_url,
        source=payload.source,
        notes=payload.notes,
    )
    for point in payload.points:
        verification.points.append(QuotePoint(**point.model_dump()))
    session.add(verification)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=409, detail="montante duplicado na mesma ronda")
    session.refresh(verification)
    return verification


@router.get("/verifications", response_model=list[VerificationOut])
def list_verifications(
    provider_id: int | None = None,
    limit: int = Query(default=20, ge=1, le=200),
    session: Session = Depends(get_session),
    _: None = Depends(require_admin),
) -> list[Verification]:
    query = (
        select(Verification)
        .options(selectinload(Verification.points))
        .order_by(Verification.verified_at.desc(), Verification.id.desc())
        .limit(limit)
    )
    if provider_id is not None:
        query = query.where(Verification.provider_id == provider_id)
    return list(session.scalars(query).all())