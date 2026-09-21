from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Provider

PROVIDERS: list[dict] = [
    {"slug": "wise", "name": "Wise", "website": "https://wise.com"},
    {"slug": "remitly", "name": "Remitly", "website": "https://www.remitly.com"},
    {"slug": "worldremit", "name": "WorldRemit", "website": "https://www.worldremit.com"},
    {"slug": "ria", "name": "Ria", "website": "https://www.riamoneytransfer.com"},
    {"slug": "westernunion", "name": "Western Union", "website": "https://www.westernunion.com"},
    {"slug": "moneygram", "name": "MoneyGram", "website": "https://www.moneygram.com"},
]


def seed_providers(session: Session) -> None:
    existing = set(session.scalars(select(Provider.slug)).all())
    for data in PROVIDERS:
        if data["slug"] not in existing:
            session.add(Provider(**data))
    session.commit()