from dataclasses import dataclass, field
from decimal import Decimal


class CollectorError(Exception):
    """Falha ao recolher cotações de um provedor. Nunca inventar dados."""


@dataclass(frozen=True)
class PointData:
    amount_eur: Decimal
    received_cve: Decimal
    fee_eur: Decimal | None = None
    pct_fee: Decimal | None = None
    fx_rate: Decimal | None = None
    payment_method: str | None = None
    payout_method: str | None = None
    delivery_time: str | None = None


@dataclass
class CollectorResult:
    provider_slug: str
    source_url: str
    notes: str | None = None
    points: list[PointData] = field(default_factory=list)


class Collector:
    slug: str = ""
    name: str = ""

    def collect(self) -> CollectorResult:
        raise NotImplementedError