from fastapi.testclient import TestClient
import pytest


def test_ip_invalid_address(client_tcp_faked: TestClient) -> None:
    """
    Невалидный ``address`` даёт 400.

    Args:
        client_tcp_faked: Клиент с заглушкой TCP.
    """
    response = client_tcp_faked.get("/api/v1/ip", params={"address": "not-an-ip"})

    assert response.status_code == 400
    assert "detail" in response.json()


def test_ip_ipv4_json_shape(client_tcp_faked: TestClient) -> None:
    """
    Успешный ответ содержит поля гео, флага и блока reachability.

    Args:
        client_tcp_faked: Клиент с заглушкой TCP.
    """
    response = client_tcp_faked.get("/api/v1/ip", params={"address": "8.8.8.8"})

    assert response.status_code == 200
    body = response.json()
    assert body["ip"] == "8.8.8.8"
    assert "geo" in body
    assert "flag_emoji" in body
    assert "reachability" in body
    assert body["reachability"]["reachable"] is True
    assert body["reachability"]["method"] == "tcp:443"

    if body["geo"].get("country_iso") is not None:
        assert body["flag_emoji"] is not None


def test_ip_ipv6(client_tcp_faked: TestClient) -> None:
    """
    IPv6 нормализуется в ответе.

    Args:
        client_tcp_faked: Клиент с заглушкой TCP.
    """
    response = client_tcp_faked.get(
        "/api/v1/ip",
        params={"address": "2001:4860:4860::8888"})

    assert response.status_code == 200
    assert response.json()["ip"] == "2001:4860:4860::8888"
