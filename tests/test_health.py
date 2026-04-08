from fastapi.testclient import TestClient


def test_health_ok(client: TestClient) -> None:
    """
    ``GET /health`` возвращает 200 и поле ``status``.

    Args:
        client: Клиент приложения.
    """
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
