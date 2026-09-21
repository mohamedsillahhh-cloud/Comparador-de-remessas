from decimal import Decimal

from pydantic_settings import BaseSettings, SettingsConfigDict

REFERENCE_AMOUNTS: tuple[int, ...] = (100, 250, 500, 1000, 2000)
PARITY_CVE_PER_EUR: Decimal = Decimal("110.265")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg://comparador:comparador@localhost:5432/comparador"
    admin_token: str = "dev-admin-token"
    cors_origins: str = "http://localhost:5173"
    stale_after_days: int = 7

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


_settings: Settings | None = None


def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings