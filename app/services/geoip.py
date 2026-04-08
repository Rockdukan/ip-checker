from dataclasses import dataclass
from pathlib import Path

import geoip2.database
import geoip2.errors


@dataclass
class GeoipRecord:
    """Сводка по геолокации и ASN для одного IP."""
    country_name_en: str | None
    country_iso: str | None
    city_name_en: str | None
    subdivisions_en: tuple[str, ...]
    latitude: float | None
    longitude: float | None
    postal_code: str | None
    timezone: str | None
    asn_number: int | None
    asn_organization: str | None


class GeoipService:
    """
    Загружает читатели MMDB из каталога и отдаёт агрегированную информацию по IP.

    Notes:
        Отсутствующие файлы или записи не считаются ошибкой: поля остаются пустыми.
    """
    def __init__(self, data_dir: Path) -> None:
        self.city_reader: geoip2.database.Reader | None = None
        self.country_reader: geoip2.database.Reader | None = None
        self.asn_reader: geoip2.database.Reader | None = None

        city_path = data_dir / "city.mmdb"
        country_path = data_dir / "country.mmdb"
        asn_path = data_dir / "asn.mmdb"

        if city_path.is_file():
            self.city_reader = geoip2.database.Reader(str(city_path))

        if country_path.is_file():
            self.country_reader = geoip2.database.Reader(str(country_path))

        if asn_path.is_file():
            self.asn_reader = geoip2.database.Reader(str(asn_path))

    def close(self) -> None:
        """Закрывает все открытые читатели MMDB."""
        for reader in (self.city_reader, self.country_reader, self.asn_reader):
            if reader is not None:
                reader.close()

        self.city_reader = None
        self.country_reader = None
        self.asn_reader = None

    def lookup(self, ip: str) -> GeoipRecord:
        """
        Собирает данные из city/country/asn баз для переданного IP.

        Args:
            ip: Допустимый IPv4 или IPv6 в строковой форме.

        Returns:
            Заполненный или частично пустой ``GeoipRecord``.
        """
        country_name: str | None = None
        country_iso: str | None = None
        city_name: str | None = None
        subdivisions: list[str] = []
        latitude: float | None = None
        longitude: float | None = None
        postal: str | None = None
        timezone: str | None = None
        asn_number: int | None = None
        asn_org: str | None = None

        if self.city_reader is not None:
            try:
                city = self.city_reader.city(ip)
                country_name = city.country.name
                country_iso = city.country.iso_code
                city_name = city.city.name
                subdivisions = [s.name for s in city.subdivisions if s.name]
                latitude = city.location.latitude
                longitude = city.location.longitude
                postal = city.postal.code if city.postal is not None else None
                timezone = city.location.time_zone
            except geoip2.errors.AddressNotFoundError:
                pass

        if country_iso is None and self.country_reader is not None:
            try:
                country = self.country_reader.country(ip)
                country_name = country.country.name
                country_iso = country.country.iso_code
            except geoip2.errors.AddressNotFoundError:
                pass

        if self.asn_reader is not None:
            try:
                asn = self.asn_reader.asn(ip)
                asn_number = asn.autonomous_system_number
                asn_org = asn.autonomous_system_organization
            except geoip2.errors.AddressNotFoundError:
                pass

        return GeoipRecord(
            country_name_en=country_name,
            country_iso=country_iso,
            city_name_en=city_name,
            subdivisions_en=tuple(subdivisions),
            latitude=latitude,
            longitude=longitude,
            postal_code=postal,
            timezone=timezone,
            asn_number=asn_number,
            asn_organization=asn_org)
