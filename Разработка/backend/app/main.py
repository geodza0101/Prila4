"""
GymFuel AI — FastAPI entry point.

Собирает middleware (CORS, rate limiting placeholder, request-id),
подключает роутеры, отдаёт /health и /.
"""

from __future__ import annotations

import logging
import os
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api import auth, meals, profile, recognize

# -----------------------------------------------------------------
# Конфиг
# -----------------------------------------------------------------
API_PREFIX: str = os.getenv("API_PREFIX", "/api")
CORS_ORIGINS: list[str] = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
    if origin.strip()
]
LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO").upper()
ENV: str = os.getenv("ENV", "development")

logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("gymfuel")


# -----------------------------------------------------------------
# Lifespan — стартап / шатдаун (инициализация клиентов БД, Redis)
# -----------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Инициализация при старте, cleanup при остановке."""
    logger.info("GymFuel backend starting (env=%s)", ENV)
    # TODO: инициализация Supabase-клиента, Redis, прогрев кеша продуктов
    yield
    logger.info("GymFuel backend shutting down")
    # TODO: закрытие пулов соединений


# -----------------------------------------------------------------
# FastAPI app
# -----------------------------------------------------------------
app = FastAPI(
    title="GymFuel AI API",
    description="AI-счётчик калорий и спортпита для людей из тренажёрного зала.",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# -----------------------------------------------------------------
# Middleware
# -----------------------------------------------------------------
# CORS — whitelist фронтендов из env
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
)


@app.middleware("http")
async def rate_limit_placeholder(request: Request, call_next):
    """
    Placeholder rate-limiter.

    В продакшене заменить на `slowapi` с лимитами по тарифу:
    - free: 60 req/min
    - pro:  300 req/min
    """
    # TODO: определить user_id / tier из JWT, проверить счётчик в Redis
    response = await call_next(request)
    return response


# -----------------------------------------------------------------
# Глобальный обработчик ошибок
# -----------------------------------------------------------------
@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled exception on %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=500,
        content={
            "error": "internal_server_error",
            "detail": "Internal server error" if ENV == "production" else str(exc),
        },
    )


# -----------------------------------------------------------------
# Системные endpoints
# -----------------------------------------------------------------
@app.get("/", tags=["system"])
async def root() -> dict[str, str]:
    """Корень — простая маркерная страница."""
    return {
        "service": "gymfuel-backend",
        "version": app.version,
        "docs": "/docs",
    }


@app.get("/health", tags=["system"])
async def health() -> dict[str, str]:
    """Liveness probe. TODO: проверить Supabase + Redis."""
    return {"status": "ok", "env": ENV}


# -----------------------------------------------------------------
# Подключение роутов
# -----------------------------------------------------------------
app.include_router(auth.router, prefix=f"{API_PREFIX}/auth", tags=["auth"])
app.include_router(profile.router, prefix=f"{API_PREFIX}/profile", tags=["profile"])
app.include_router(meals.router, prefix=f"{API_PREFIX}/meals", tags=["meals"])
app.include_router(recognize.router, prefix=f"{API_PREFIX}/recognize", tags=["recognize"])
