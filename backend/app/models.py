from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Provider(Base):
    __tablename__ = "providers"

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(128))
    website: Mapped[str] = mapped_column(Text)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    notes: Mapped[str | None] = mapped_column(Text)

    verifications: Mapped[list["Verification"]] = relationship(
        back_populates="provider", cascade="all, delete-orphan"
    )


class Verification(Base):
    __tablename__ = "verifications"

    id: Mapped[int] = mapped_column(primary_key=True)
    provider_id: Mapped[int] = mapped_column(ForeignKey("providers.id"), index=True)
    verified_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    source_url: Mapped[str] = mapped_column(Text)
    source: Mapped[str] = mapped_column(String(16), default="manual")
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    provider: Mapped["Provider"] = relationship(back_populates="verifications")
    points: Mapped[list["QuotePoint"]] = relationship(
        back_populates="verification", cascade="all, delete-orphan", order_by="QuotePoint.amount_eur"
    )


class QuotePoint(Base):
    __tablename__ = "quote_points"
    __table_args__ = (
        UniqueConstraint("verification_id", "amount_eur", name="uq_verification_amount"),
        CheckConstraint("amount_eur > 0", name="ck_amount_positive"),
        CheckConstraint("received_cve > 0", name="ck_received_positive"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    verification_id: Mapped[int] = mapped_column(ForeignKey("verifications.id"), index=True)
    amount_eur: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    received_cve: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    fee_eur: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    pct_fee: Mapped[Decimal | None] = mapped_column(Numeric(8, 4))
    fx_rate: Mapped[Decimal | None] = mapped_column(Numeric(14, 6))
    payment_method: Mapped[str | None] = mapped_column(String(128))
    payout_method: Mapped[str | None] = mapped_column(String(128))
    delivery_time: Mapped[str | None] = mapped_column(String(128))

    verification: Mapped["Verification"] = relationship(back_populates="points")