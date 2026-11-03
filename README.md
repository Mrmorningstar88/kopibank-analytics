# kopibank-analytics

Анализ воронки открытия карт Копибанка: где клиенты отваливаются и почему.

## Настройка

Settings → Secrets and variables → Actions:

| Тип | Имя | Что это |
|---|---|---|
| **Secret** | `KOPIBANK_API_TOKEN` | токен API админки, **только на чтение** |
| Variable | `KOPIBANK_API_URL` | базовый URL API, например `https://admin.kopibank.example/api` |
| Variable | `KOPIBANK_APPLICATIONS_PATH` | путь к списку заявок на карты (по умолчанию `/applications`) |

Токен — только в Secrets: значения Variables видны в настройках и логах.

## Запуск

Actions → **Funnel report** → Run workflow. Отчёт появится в Summary запуска и в артефакте `funnel-report`.

Галочка `demo` прогоняет отчёт на `samples/demo.csv` — проверить, что всё работает, до подключения API.

Локально:

```bash
python run_report.py --csv samples/demo.csv
```

## Что подогнать под реальный API

- `kopibank/client.py` — авторизация, параметры фильтра по дате, структура ответа и пагинация.
- `kopibank/funnel.py` — `STAGES` (реальные статусы заявки по порядку) и `SEGMENT_FIELDS`.

Персональные данные (ФИО, телефоны, паспорта) для анализа не нужны — лучше, чтобы API их не отдавал.
