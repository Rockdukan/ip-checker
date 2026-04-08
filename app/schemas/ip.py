from pydantic import BaseModel, Field


class AsnBlock(BaseModel):
    """Автономная система по данным ASN MMDB."""
    number: int | None = None
    organization: str | None = None


class GeoBlock(BaseModel):
    """Геоданные из City/Country MMDB."""
    country: str | None = None
    country_iso: str | None = None
    city: str | None = None
    subdivisions: list[str] = Field(default_factory=list)
    latitude: float | None = None
    longitude: float | None = None
    postal_code: str | None = None
    timezone: str | None = None


class ReachabilityBlock(BaseModel):
    """Результат проверки доступности узла по TCP."""
    reachable: bool
    method: str | None = None
    latency_ms: float | None = None


class IpLookupResponse(BaseModel):
    """Полный ответ по одному IP: гео, ASN, флаг, доступность."""
    ip: str
    flag_emoji: str | None = None
    geo: GeoBlock
    asn: AsnBlock | None = None
    reachability: ReachabilityBlock
