"""
Auth endpoints.

Регистрация / вход / выход / обновление токена.
По ТЗ — auth делегирован в Supabase Auth, backend только проксирует
и добавляет наши бизнес-проверки (email verification, invite-коды и т.д.).
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from app.models.schemas import (
    AuthTokenResponse,
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    UserPublic,
)

router = APIRouter()


# -----------------------------------------------------------------
# POST /api/auth/register
# -----------------------------------------------------------------
@router.post(
    "/register",
    response_model=AuthTokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Регистрация пользователя",
)
async def register(payload: RegisterRequest) -> AuthTokenResponse:
    """
    Создаёт нового пользователя через Supabase Auth.

    После регистрации отправляется email-верификация.
    Возвращает access/refresh токены.
    """
    # TODO: supabase.auth.sign_up(email=payload.email, password=payload.password)
    # TODO: создать запись в users (subscription='free')
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="register: not implemented",
    )


# -----------------------------------------------------------------
# POST /api/auth/login
# -----------------------------------------------------------------
@router.post(
    "/login",
    response_model=AuthTokenResponse,
    summary="Вход по email+password",
)
async def login(payload: LoginRequest) -> AuthTokenResponse:
    """Аутентификация через Supabase Auth → access + refresh токены."""
    # TODO: supabase.auth.sign_in_with_password(...)
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="login: not implemented",
    )


# -----------------------------------------------------------------
# POST /api/auth/logout
# -----------------------------------------------------------------
@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Выход (инвалидация refresh-токена)",
)
async def logout() -> None:
    """Инвалидирует refresh-токен у Supabase."""
    # TODO: извлечь токен из Authorization header, supabase.auth.sign_out(...)
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="logout: not implemented",
    )


# -----------------------------------------------------------------
# POST /api/auth/refresh
# -----------------------------------------------------------------
@router.post(
    "/refresh",
    response_model=AuthTokenResponse,
    summary="Обновить access-токен",
)
async def refresh(payload: RefreshRequest) -> AuthTokenResponse:
    """Возвращает новую пару access/refresh по действительному refresh-токену."""
    # TODO: supabase.auth.refresh_session(payload.refresh_token)
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="refresh: not implemented",
    )


# -----------------------------------------------------------------
# GET /api/auth/me — бонусный endpoint для фронта
# -----------------------------------------------------------------
@router.get(
    "/me",
    response_model=UserPublic,
    summary="Текущий пользователь (по Bearer-токену)",
)
async def me() -> UserPublic:
    """Вернуть данные текущего пользователя по JWT из Authorization header."""
    # TODO: зависимость get_current_user(token) → UserPublic
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="me: not implemented",
    )
