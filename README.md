# ip-checker

Микросервис на FastAPI: геоданные по IP из локальных баз MaxMind GeoIP2 (`*.mmdb`), эмодзи флага страны, проверка **TCP-достижимости** узла (последовательная попытка `connect()` к портам **443** и **80** на транспортном уровне, без TLS и без ICMP).

## `GET /health`

- Ответ: `{"status": "ok"}`.
- Использование: liveness/readiness в Kubernetes, healthcheck в Docker, проверки балансировщиков.

## API

| Метод | Описание |
|--------|-----------|
| `GET /api/v1/ip` | Query: `address` (IPv4 или IPv6); опционально `tcp_timeout` (сек., по умолчанию 3). Ответ: гео, ASN при наличии MMDB, флаг, результат TCP `connect()` (443, затем 80). |

## Базы GeoIP

Каталог с файлами MMDB задаётся переменной **`MMDB_DIR`** (по умолчанию: `<корень репозитория>/data`).

Ожидаемые имена (недостающие файлы игнорируются):

- `city.mmdb`
- `country.mmdb`
- `asn.mmdb`

## Флаги

Словарь `COUNTRY_FLAGS`: [`app/country_flags.py`](app/country_flags.py).

```python
from app.country_flags import COUNTRY_FLAGS
```

## Запуск локально

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
MMDB_DIR=./data uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Тесты

```bash
source .venv/bin/activate
pip install -r requirements-dev.txt
pytest
```

## Docker

[`Dockerfile`](Dockerfile): `MMDB_DIR=/app/data`, каталог `data` — при сборке или через volume.
