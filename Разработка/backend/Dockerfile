# syntax=docker/dockerfile:1.7
# ============================================================
# GymFuel AI Backend — multi-stage production image
# ============================================================

# -------- Stage 1: builder ---------------------------------
FROM python:3.11-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Системные зависимости для сборки (bcrypt, cryptography)
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        gcc \
        libffi-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /build

# Копируем только метаданные — использование Docker layer cache
COPY pyproject.toml README.md ./

# Установка в изолированный префикс — потом скопируем в runtime
RUN pip install --upgrade pip setuptools wheel \
    && pip install --prefix=/install ".[dev]" --no-deps \
    && pip install --prefix=/install \
        "fastapi>=0.115.0" \
        "uvicorn[standard]>=0.32.0" \
        "pydantic>=2.9.0" \
        "pydantic-settings>=2.6.0" \
        "python-multipart>=0.0.18" \
        "supabase>=2.9.0" \
        "httpx>=0.28.0" \
        "redis>=5.2.0" \
        "python-jose[cryptography]>=3.3.0" \
        "passlib[bcrypt]>=1.7.4" \
        "python-dotenv>=1.0.1" \
        "structlog>=24.4.0" \
        "slowapi>=0.1.9" \
        "tenacity>=9.0.0" \
        "orjson>=3.10.0"

# -------- Stage 2: runtime ---------------------------------
FROM python:3.11-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/usr/local/bin:$PATH" \
    PORT=8000

# Минимум системных либ для рантайма
RUN apt-get update && apt-get install -y --no-install-recommends \
        curl \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Non-root user — security best practice
RUN groupadd --system --gid 1001 app \
    && useradd --system --uid 1001 --gid app --create-home --home-dir /home/app app

# Копируем установленные пакеты из builder
COPY --from=builder /install /usr/local

WORKDIR /app

# Копируем исходники (владелец — non-root)
COPY --chown=app:app app ./app
COPY --chown=app:app pyproject.toml README.md ./

USER app

EXPOSE 8000

# Health-check — Docker сам проверит /health
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -fsS "http://127.0.0.1:${PORT}/health" || exit 1

# uvicorn без --reload в проде, workers через ENV
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT} --workers ${UVICORN_WORKERS:-2}"]
