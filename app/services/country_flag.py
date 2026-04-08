from app.country_flags import COUNTRY_FLAGS


def flag_from_iso3166_alpha2(iso_code: str | None) -> str | None:
    """
    Формирует эмодзи флага по коду ISO 3166-1 alpha-2 (два латинских символа).

    Args:
        iso_code: Двухсимвольный код страны, например ``RU`` или ``us`` (регистр не важен).

    Returns:
        Строка из двух региональных индикаторов Unicode или ``None``, если код невалиден.

    Notes:
        Не покрывает составные флаги (Шотландия, Англия и т.п.) — для них используется
        словарь ``app.country_flags.COUNTRY_FLAGS``.
    """
    if iso_code is None:
        return None

    code = iso_code.strip().upper()

    if len(code) != 2 or not code.isalpha():
        return None

    return chr(0x1F1E6 + ord(code[0]) - ord("A")) + chr(0x1F1E6 + ord(code[1]) - ord("A"))


def resolve_country_flag(country_name_en: str | None, iso_code: str | None) -> str | None:
    """
    Возвращает эмодзи флага по английскому названию из GeoIP либо по ISO alpha-2.

    Args:
        country_name_en: Название страны на английском, как в базе GeoIP.
        iso_code: Код ISO 3166-1 alpha-2.

    Returns:
        Эмодзи флага или ``None``, если определить не удалось.
    """
    if country_name_en:
        direct = COUNTRY_FLAGS.get(country_name_en)

        if direct is not None:
            return direct

    return flag_from_iso3166_alpha2(iso_code)
