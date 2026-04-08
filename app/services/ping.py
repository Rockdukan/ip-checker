import asyncio
from collections.abc import Sequence
import time

DEFAULT_TCP_PORTS: tuple[int, ...] = (443, 80)
DEFAULT_TIMEOUT_SECONDS: float = 3.0


async def check_tcp_reachability(
    host: str,
    ports: Sequence[int] | None = None,
    timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS) -> tuple[bool, str | None, float | None]:
    """
    Пытается установить TCP-соединение с указанными портами по очереди.

    Args:
        host: IP-адрес или имя хоста.
        ports: TCP-порты для ``connect()``; по умолчанию 443, затем 80 (не TLS/HTTP(S), только сокет).
        timeout_seconds: Таймаут на одну попытку подключения.

    Returns:
        Кортеж ``(успех, метод/описание, задержка_мс)``. При неудаче задержка ``None``.
    """
    port_list = tuple(ports or DEFAULT_TCP_PORTS)

    for port in port_list:
        label = f"tcp:{port}"
        started = time.perf_counter()

        try:
            connect_coro = asyncio.open_connection(host, port)
            reader, writer = await asyncio.wait_for(connect_coro, timeout=timeout_seconds)
            writer.close()
            await writer.wait_closed()
            elapsed_ms = round((time.perf_counter() - started) * 1000.0, 3)
            return True, label, elapsed_ms
        except (asyncio.TimeoutError, OSError, ConnectionError):
            continue

    return False, None, None
