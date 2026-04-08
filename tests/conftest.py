from collections.abc import Generator
import os
from pathlib import Path

from fastapi.testclient import TestClient
import pytest

ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="session", autouse=True)
def mmdb_dir() -> Path:
    """
    Выставляет ``MMDB_DIR`` до импорта приложения тестами.

    Returns:
        Путь к каталогу с ``*.mmdb`` в репозитории.
    """
    data = ROOT / "data"
    os.environ["MMDB_DIR"] = str(data)

    return data


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    """
    Синхронный TestClient без подмены сетевого слоя.

    Yields:
        Клиент FastAPI.
    """
    from app.main import app

    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def client_tcp_faked(monkeypatch: pytest.MonkeyPatch) -> Generator[TestClient, None, None]:
    """
    TestClient с заглушкой ``check_tcp_reachability`` (без реального ``connect()``).

    Yields:
        Клиент FastAPI.
    """
    async def fake_tcp_reachability(*args: object, **kwargs: object) -> tuple[bool, str, float]:
        return True, "tcp:443", 1.0

    monkeypatch.setattr(
        "app.api.v1.ip.check_tcp_reachability",
        fake_tcp_reachability)
    from app.main import app

    with TestClient(app) as test_client:
        yield test_client
