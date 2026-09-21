from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ProviderOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    slug: str
    name: str
    website: str
    active: bool
    notes: str | None = None


class MetaOut(BaseModel):
    parity_cve_per_eur: float
    stale_after_days: int
    reference_amounts: list[int]


class QuoteOut(BaseModel):
    provider_id: int
    provider_slug: str
    provider_name: str
    provider_website: str
    amount_eur: float
    received_cve: float
    effective_rate: float
    parity_rate: float
    margin_pct: float
    cost_eur: float
    fee_eur: float | None = None
    pct_fee: float | None = None
    fx_rate: float | None = None
    payment_method: str | None = None
    payout_method: str | None = None
    delivery_time: str | None = None
    verified_at: datetime
    source_url: str
    source: str
    estimated: bool
    stale: bool


class ProviderCreate(BaseModel):
    slug: str = Field(min_length=2, max_length=64, pattern=r"^[a-z0-9-]+$")
    name: str = Field(min_length=2)
    website: str = Field(min_length=1)
    notes: str | None = None


class ProviderUpdate(BaseModel):
    name: str | None = None
    website: str | None = None
    active: bool | None = None
    notes: str | None = None


class PointIn(BaseModel):
    amount_eur: Decimal = Field(gt=0)
    received_cve: Decimal = Field(gt=0)
    fee_eur: Decimal | None = Field(default=None, gt=0)
    pct_fee: Decimal | None = Field(default=None, ge=0, le=100)
    fx_rate: Decimal | None = Field(default=None, gt=0)
    payment_method: str | None = None
    payout_method: str | None = None
    delivery_time: str | None = None


class VerificationIn(BaseModel):
    provider_id: int
    source_url: str = Field(min_length=1)
    source: Literal["manual", "auto"] = "manual"
    notes: str | None = None
    verified_at: datetime | None = None
    points: list[PointIn] = Field(min_length=1)


class PointOut(BaseModel):
    amount_eur: float
    received_cve: float
    fee_eur: float | None = None
    pct_fee: float | None = None
    fx_rate: float | None = None
    payment_method: str | None = None
    payout_method: str | None = None
    delivery_time: str | None = None


class VerificationOut(BaseModel):
    id: int
    provider_id: int
    verified_at: datetime
    source_url: str
    source: str
    notes: str | None = None
    created_at: datetime
    points: list[PointOut] = []