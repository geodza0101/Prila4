# GymFuel AI — Backend

FastAPI-бэкенд для AI-счётчика калорий и спортпита GymFuel AI.

## Стек

- **Python 3.11+** — язык
- **FastAPI** — web-фреймворк (async)
- **Pydantic v2** — валидация схем
- **Supabase Python client** — PostgreSQL + Auth + Storage + pgvector
- **httpx** — async HTTP-клиент для интеграций (USDA / OFF / Gemini)
- **Redis** — кеш распознавания и агрегатов дня
- **pytest + pytest-asyncio** — тесты
- **uv** или **pip** — менеджер пакетов

## Структура

```
backend/
├── app/
│   ├── main.py               # FastAPI entry point, middleware, routes
│   ├── api/                  # HTTP endpoints
│   │   ├── auth.py           # /api/auth/*
│   │   ├── profile.py        # /api/profile/*
│   │   ├── meals.py          # /api/meals/*
│   │   └── recognize.py      # /api/recognize/*
│   ├── services/             # Бизнес-логика
│   │   └── nutrition.py      # BMR / TDEE / targets — чистые функции
│   ├── models/               # Pydantic-схемы
│   │   └── schemas.py
│   ├── db/                   # Клиент Supabase (заглушка)
│   ├── integrations/         # USDA / OFF / Gemini (заглушки)
│   └── utils/
├── supabase/
│   └── migrations/
│       └── 0001_initial_schema.sql
├── tests/
│   └── test_nutrition.py
├── pyproject.toml
├── Dockerfile
├── docker-compose.yml
├── .env.example
└── README.md
```

## Быстрый старт (локально)

### 1. Установка зависимостей

```bash
# через uv (рекомендуется)
uv sync

# или через pip
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

### 2. Переменные окружения

```bash
cp .env.example .env
# заполнить реальными ключами (SUPABASE_URL, SUPABASE_ANON_KEY, GEMINI_API_KEY, ...)
```

### 3. Миграции Supabase

```bash
# через supabase CLI
supabase db push

# или вручную через SQL Editor
# скопировать содержимое supabase/migrations/0001_initial_schema.sql
```

### 4. Запуск сервера разработки

```bash
uvicorn app.main:app --reload --port 8000
```

Swagger: http://localhost:8000/docs
Health-check: http://localhost:8000/health

### 5. Тесты

```bash
pytest -v
pytest tests/test_nutrition.py -v
pytest --cov=app --cov-report=term-missing
```

## Docker

```bash
docker-compose up --build
```

Поднимет: `backend` (FastAPI на :8000) + `redis` (:6379).

## API Endpoints (MVP)

| Метод | Путь | Описание |
|-------|------|----------|
| POST  | `/api/auth/register`        | Регистрация email+password |
| POST  | `/api/auth/login`           | Вход |
| POST  | `/api/auth/logout`          | Выход |
| POST  | `/api/auth/refresh`         | Обновить токен |
| GET   | `/api/profile`              | Мой профиль |
| POST  | `/api/profile`              | Создать/обновить профиль |
| POST  | `/api/profile/recalculate`  | Пересчитать нормы КБЖУ |
| GET   | `/api/meals?date=YYYY-MM-DD`| Приёмы пищи за день |
| POST  | `/api/meals`                | Добавить приём |
| PATCH | `/api/meals/{id}`           | Обновить приём |
| DELETE| `/api/meals/{id}`           | Удалить приём |
| POST  | `/api/recognize/photo`      | Распознать еду по фото |

Полная спецификация — в Swagger UI (`/docs`).

## Формулы расчёта норм

См. `app/services/nutrition.py`:

- **BMR** — Mifflin-St Jeor
- **TDEE** — BMR × коэффициент активности (1.375 / 1.55 / 1.725)
- **Target calories** — TDEE × {1.15 массонабор / 1.0 поддержка / 0.80 сушка}
- **Protein** — {2.0 / 1.8 / 2.3} г/кг
- **Fat** — 0.9 г/кг
- **Carbs** — остаток от калорий

## Безопасность

- JWT через Supabase Auth
- Row-Level Security (RLS) на всех пользовательских таблицах
- Rate limiting (60 req/min free, 300/min pro) — middleware placeholder
- Секреты только через env vars — никогда не коммитить `.env`
- CORS whitelist для фронтенда

## Что НЕ входит в MVP (см. ТЗ раздел 14)

- Голосовой ввод
- Barcode scanner
- AI-диетолог (Claude Sonnet)
- Интеграция Apple Health / Google Fit
- Платёжный модуль

## Ссылки

- ТЗ: `../../Техническое задание.md`
- Идея: `../../Идея.md`
- Исследование: `../../Исследование.md`
