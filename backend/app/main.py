from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.db import SessionLocal
from app.routers import admin, public
from app.seed import seed_providers


@asynccontextmanager
async def lifespan(_: FastAPI):
    with SessionLocal() as session:
        seed_providers(session)
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title="Comparador de Remessas API", lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(public.router)
    app.include_router(admin.router)
    return app


app = create_app()