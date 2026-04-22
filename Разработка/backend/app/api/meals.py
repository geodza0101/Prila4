"""
Meals endpoints — дневник питания.

Каждый приём пищи — строка в таблице `meals` с привязкой к food_id.
КБЖУ считаются на бэке при создании (grams × food.*_per_100g / 100).
"""

from __future__ import annotations

from datetime import date as DateType
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status

from app.models.schemas import MealCreate, MealResponse, MealUpdate

router = APIRouter()


# -----------------------------------------------------------------
# GET /api/meals?date=YYYY-MM-DD
# -----------------------------------------------------------------
@router.get(
    "",
    response_model=list[MealResponse],
    summary="Приёмы пищи за день",
)
async def list_meals(
    date: DateType = Query(..., description="Дата в формате YYYY-MM-DD"),
) -> list[MealResponse]:
    """Вернуть все приёмы пищи текущего пользователя за указанный день."""
    # TODO: supabase.table("meals").select("*, foods(*)").eq("user_id", uid).eq("date", date)
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="list_meals: not implemented",
    )


# -----------------------------------------------------------------
# POST /api/meals
# -----------------------------------------------------------------
@router.post(
    "",
    response_model=MealResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Добавить приём пищи",
)
async def create_meal(payload: MealCreate) -> MealResponse:
    """
    Создать запись приёма пищи.

    Бэк:
    1. Читает food (по food_id) — получает *_per_100g.
    2. Считает kcal/protein/carbs/fat = grams × per_100g / 100.
    3. Вставляет в `meals`.
    """
    # TODO: food = supabase.table("foods").select("*").eq("id", payload.food_id).single()
    # TODO: if not food: raise HTTPException(404, "Food not found")
    # TODO: compute nutrients; insert row; return
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="create_meal: not implemented",
    )


# -----------------------------------------------------------------
# PATCH /api/meals/{id}
# -----------------------------------------------------------------
@router.patch(
    "/{meal_id}",
    response_model=MealResponse,
    summary="Обновить приём пищи",
)
async def update_meal(meal_id: UUID, payload: MealUpdate) -> MealResponse:
    """Частичное обновление. При изменении grams — пересчёт КБЖУ."""
    # TODO: проверить ownership (user_id), apply changes, recompute nutrients
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="update_meal: not implemented",
    )


# -----------------------------------------------------------------
# DELETE /api/meals/{id}
# -----------------------------------------------------------------
@router.delete(
    "/{meal_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить приём пищи",
)
async def delete_meal(meal_id: UUID) -> None:
    """Жёсткое удаление (RLS не даст удалить чужой)."""
    # TODO: supabase.table("meals").delete().eq("id", meal_id)
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="delete_meal: not implemented",
    )
