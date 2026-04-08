import pytest

from app.services.country_flag import flag_from_iso3166_alpha2, resolve_country_flag


@pytest.mark.parametrize(
    ("name", "iso", "expected_contains"),
    [
        ("United States", "US", "🇺🇸"),
        ("Germany", "DE", "🇩🇪"),
        (None, "UA", "🇺🇦"),
    ],
)
def test_resolve_country_flag(name: str | None, iso: str | None, expected_contains: str) -> None:
    """
    Словарь имён и fallback по ISO дают ожидаемый символ флага.

    Args:
        name: Английское имя страны из GeoIP или ``None``.
        iso: Код ISO 3166-1 alpha-2.
        expected_contains: Ожидаемая подстрока (один эмодзи).
    """
    result = resolve_country_flag(name, iso)

    assert result is not None
    assert expected_contains in result


def test_flag_invalid_iso() -> None:
    """Невалидный ISO не даёт флага."""
    assert flag_from_iso3166_alpha2(None) is None
    assert flag_from_iso3166_alpha2("ZZZ") is None
    assert flag_from_iso3166_alpha2("1A") is None
