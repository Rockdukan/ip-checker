import ipaddress
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Request

from app.schemas.ip import AsnBlock, GeoBlock, IpLookupResponse, ReachabilityBlock
from app.services.country_flag import resolve_country_flag
from app.services.geoip import GeoipService
from app.services.ping import check_tcp_reachability

router = APIRouter()


def get_geoip_service(request: Request) -> GeoipService:
    """
    Достаёт сервис GeoIP из состояния приложения.

    Args:
        request: Текущий HTTP-запрос FastAPI.

    Returns:
        Инициализированный ``GeoipService``.

    Raises:
        HTTPException: если сервис не смонтирован в ``app.state`` (конфигурация).
    """
    geoip = getattr(request.app.state, "geoip", None)

    if geoip is None:
        raise HTTPException(status_code=500, detail="Сервис GeoIP не инициализирован.")

    return geoip


@router.get("", response_model=IpLookupResponse)
async def lookup_ip(
    address: Annotated[str, Query(description="IPv4 или IPv6 адрес.")],
    geoip: GeoipService = Depends(get_geoip_service),
    tcp_timeout: Annotated[float, Query(gt=0.0, le=30.0, description="Таймаут TCP, сек.")] = 3.0) -> IpLookupResponse:
    """
    Возвращает геоданные MMDB, эмодзи флага и признак TCP-достижимости (connect к 443, затем 80; L4, не HTTPS).

    Args:
        address: Произвольная строка с IP; пробелы по краям допускаются.
        geoip: Сервис чтения MMDB.
        tcp_timeout: Верхняя граница ожидания на одну попытку TCP.

    Returns:
        Сводная модель ``IpLookupResponse``.

    Raises:
        HTTPException: 400 при невалидном IP.
    """
    try:
        normalized = str(ipaddress.ip_address(address.strip()))
    except ValueError:
        raise HTTPException(status_code=400, detail="Некорректный IP-адрес.") from None

    record = geoip.lookup(normalized)
    flag = resolve_country_flag(record.country_name_en, record.country_iso)
    reachable, method, latency_ms = await check_tcp_reachability(
        normalized,
        timeout_seconds=tcp_timeout)

    geo = GeoBlock(
        country=record.country_name_en,
        country_iso=record.country_iso,
        city=record.city_name_en,
        subdivisions=list(record.subdivisions_en),
        latitude=record.latitude,
        longitude=record.longitude,
        postal_code=record.postal_code,
        timezone=record.timezone)

    asn: AsnBlock | None = None

    if record.asn_number is not None or record.asn_organization is not None:
        asn = AsnBlock(number=record.asn_number, organization=record.asn_organization)

    reachability = ReachabilityBlock(
        reachable=reachable,
        method=method,
        latency_ms=latency_ms)

    return IpLookupResponse(
        ip=normalized,
        flag_emoji=flag,
        geo=geo,
        asn=asn,
        reachability=reachability)
