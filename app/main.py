from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
import os
from pathlib import Path

from fastapi import FastAPI

from app.api.v1 import api_router
from app.services.geoip import GeoipService


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """
    Открывает читатели MaxMind при старте и закрывает их при остановке.

    Yields:
        Управление передаётся работающему приложению.

    Notes:
        Каталог с ``*.mmdb`` задаётся переменной ``MMDB_DIR`` или по умолчанию ``<корень>/data``.
    """
    default_data = Path(__file__).resolve().parent.parent / "data"
    data_dir = Path(os.environ.get("MMDB_DIR", str(default_data)))
    geoip = GeoipService(data_dir)
    app.state.geoip = geoip

    yield

    geoip.close()


app = FastAPI(title="IP Checker", version="0.1.0", lifespan=lifespan)
app.include_router(api_router, prefix="/api/v1")


@app.get("/health", tags=["meta"])
async def health() -> dict[str, str]:
    """Минимальная ручка для балансировщиков и оркестраторов."""
    return {"status": "ok"}
