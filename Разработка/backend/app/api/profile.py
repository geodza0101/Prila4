"""
Profile endpoints.

Профиль пользователя: пол, возраст, вес, рост, цель, активность, спортпит.
При создании/обновлении — автоматический пересчёт BMR/TDEE/target КБЖУ.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from app.models.schemas import ProfileResponse, ProfileUpsertRequest

router = APIRouter()


# -----------------------------------------------------------------
# GET /api/profile
# -----------------------------------------------------------------
@router.get(
    "",
    response_model=ProfileResponse,
    summary="Мой профиль",
)
async def get_profile() -> ProfileResponse:
    """Вернуть профиль текущего пользователя со всеми расчётными нормами."""
    # TODO: user_id = current_user.id
    # TODO: row = supabase.table("profiles").select("*").eq("user_id", user_id).single()
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="get_profile: not implemented",
    )


# -----------------------------------------------------------------
# POST /api/profile  (create или update — upsert)
# -----------------------------------------------------------------
@router.post(
    "",
    response_model=ProfileResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать или обновить профиль",
)
async def upsert_profile(payload: ProfileUpsertRequest) -> ProfileResponse:
    """
    Upsert профиля.

    После записи — пересчитать BMR / TDEE / target_kcal / target_protein / ... ,
    сохранить в те же поля profiles.
    """
    # TODO: 1. валидация
    # TODO: 2. nutrition.calculate_bmr(...)
    # TODO: 3. nutrition.calculate_tdee(...)
    # TODO: 4. nutrition.calculate_targets(...)
    # TODO: 5. upsert в Supabase
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="upsert_profile: not implemented",
    )


# -----------------------------------------------------------------
# POST /api/profile/recalculate
# -----------------------------------------------------------------
@router.post(
    "/recalculate",
    response_model=ProfileResponse,
    summary="Пересчитать нормы КБЖУ",
)
async def recalculate_profile() -> ProfileResponse:
    """
    Пересчёт target_kcal / target_protein / target_carbs / target_fat
    по текущим параметрам профиля (без изменения пола/возраста/роста).

    Используется, например, после редактирования цели (bulk/cut/maintain)
    или загрузки нового веса.
    """
    # TODO: загрузить профиль → прогнать через nutrition.calculate_* → сохранить
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="recalculate_profile: not implemented",
    )
