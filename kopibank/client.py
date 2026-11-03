"""Read-only клиент API админки Копибанка.

Настройки берутся из переменных окружения (в GitHub Actions — из Secrets/Variables):
  KOPIBANK_API_URL            базовый URL API, например https://admin.kopibank.example/api
  KOPIBANK_API_TOKEN          токен только на чтение (держать в Secrets)
  KOPIBANK_APPLICATIONS_PATH  путь к списку заявок на карты, по умолчанию /applications

Формат ответа и пагинацию нужно подогнать под реальный API — см. TODO ниже.
"""

import json
import os
import urllib.parse
import urllib.request


def _config():
    url = os.environ.get("KOPIBANK_API_URL")
    token = os.environ.get("KOPIBANK_API_TOKEN")
    if not url or not token:
        raise SystemExit("Нужны переменные KOPIBANK_API_URL и KOPIBANK_API_TOKEN")
    path = os.environ.get("KOPIBANK_APPLICATIONS_PATH", "/applications")
    return url.rstrip("/"), token, path


def _get(url, token):
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {token}",  # TODO: проверить схему авторизации
        "Accept": "application/json",
    })
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.load(resp)


def fetch_applications(date_from=None, date_to=None, page_size=500):
    """Выгружает все заявки на карты за период, проходя по страницам."""
    base, token, path = _config()
    page = 1
    items = []
    while True:
        params = {"page": page, "per_page": page_size}
        if date_from:
            params["date_from"] = date_from
        if date_to:
            params["date_to"] = date_to
        data = _get(f"{base}{path}?{urllib.parse.urlencode(params)}", token)
        # TODO: поправить под реальную структуру ответа
        batch = data.get("items", data) if isinstance(data, dict) else data
        items.extend(batch)
        if len(batch) < page_size:
            return items
        page += 1
