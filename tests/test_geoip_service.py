from pathlib import Path

import pytest

from app.services.geoip import GeoipService



@pytest.fixture
def geoip_service(mmdb_dir: Path) -> GeoipService:
    """
    Сервис GeoIP на каталоге из фикстуры ``mmdb_dir``.

    Args:
        mmdb_dir: Каталог с MMDB.

    Returns:
        Открытый ``GeoipService``.
    """
    return GeoipService(mmdb_dir)


def test_geoip_lookup_google_dns(geoip_service: GeoipService) -> None:
    """
    Для 8.8.8.8 ожидается запись с ISO ``US`` при наличии city/country базы.

    Args:
        geoip_service: Сервис с локальными файлами.
    """
    if geoip_service.city_reader is None and geoip_service.country_reader is None:
        pytest.skip("Нет city.mmdb и country.mmdb")

    record = geoip_service.lookup("8.8.8.8")

    assert record.country_iso == "US"


def test_geoip_service_close_empty_dir(tmp_path: Path) -> None:
    """
    Закрытие сервиса без открытых читателей не падает.

    Args:
        tmp_path: Пустой каталог от pytest.
    """
    service = GeoipService(tmp_path)
    service.close()
