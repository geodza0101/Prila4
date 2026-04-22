"""
Nutrition — расчёт норм КБЖУ.

Чистые функции без IO. Формулы — из ТЗ раздел 2.1.3.
Все тесты — в tests/test_nutrition.py.

Источники:
- Mifflin-St Jeor (1990) — признанная формула BMR.
- Коэффициенты активности — Harris-Benedict revised.
- Нормы белка — ISSN Position Stand 2017 (Jäger et al.).
"""

from __future__ import annotations

from typing import Literal, TypedDict

# -----------------------------------------------------------------
# Типы
# -----------------------------------------------------------------
Gender = Literal["male", "female"]
ActivityLevel = Literal["low", "medium", "high"]
Goal = Literal["bulk", "maintain", "cut"]


class NutritionTargets(TypedDict):
    """Дневные целевые значения."""

    calories: int
    protein: int
    carbs: int
    fat: int


# -----------------------------------------------------------------
# Константы (из ТЗ 2.1.3)
# -----------------------------------------------------------------
# Коэффициент активности (multiplier над BMR).
# low    — 2-3 тренировки/неделя (~1.375)
# medium — 4-5 тренировок (~1.55)
# high   — 6+ тренировок (~1.725)
ACTIVITY_MULTIPLIER: dict[ActivityLevel, float] = {
    "low": 1.375,
    "medium": 1.55,
    "high": 1.725,
}

# Коэффициент калорий под цель (multiplier над TDEE).
GOAL_CALORIE_MULTIPLIER: dict[Goal, float] = {
    "bulk": 1.15,      # профицит 15%
    "maintain": 1.00,  # поддержка
    "cut": 0.80,       # дефицит 20%
}

# Норма белка (г/кг веса) под цель.
# На сушке — выше, чтобы сохранить мышечную массу при дефиците.
GOAL_PROTEIN_PER_KG: dict[Goal, float] = {
    "bulk": 2.0,
    "maintain": 1.8,
    "cut": 2.3,
}

# Норма жира (г/кг) — единая, по ТЗ "0.8-1.0 г × вес", берём середину.
FAT_PER_KG: float = 0.9

# Калорийность макросов (ккал/г).
KCAL_PER_G_PROTEIN: int = 4
KCAL_PER_G_CARBS: int = 4
KCAL_PER_G_FAT: int = 9


# -----------------------------------------------------------------
# BMR — Mifflin-St Jeor
# -----------------------------------------------------------------
def calculate_bmr(
    weight_kg: float,
    height_cm: float,
    age: int,
    gender: Gender,
) -> float:
    """
    Basal Metabolic Rate (ккал/сутки в покое).

    Формула Mifflin-St Jeor (1990):
        base = 10 × вес + 6.25 × рост − 5 × возраст
        муж:  base + 5
        жен:  base − 161

    Args:
        weight_kg: вес в кг (> 0)
        height_cm: рост в см (> 0)
        age: возраст в годах (>= 0)
        gender: "male" | "female"

    Returns:
        BMR в ккал/сутки.

    Raises:
        ValueError: если любой числовой параметр не положителен,
                    либо gender не male/female.
    """
    if weight_kg <= 0:
        raise ValueError(f"weight_kg must be > 0, got {weight_kg}")
    if height_cm <= 0:
        raise ValueError(f"height_cm must be > 0, got {height_cm}")
    if age < 0:
        raise ValueError(f"age must be >= 0, got {age}")
    if gender not in ("male", "female"):
        raise ValueError(f"gender must be 'male' or 'female', got {gender!r}")

    base = 10.0 * weight_kg + 6.25 * height_cm - 5.0 * age
    return base + 5.0 if gender == "male" else base - 161.0


# -----------------------------------------------------------------
# TDEE — Total Daily Energy Expenditure
# -----------------------------------------------------------------
def calculate_tdee(bmr: float, activity_level: ActivityLevel) -> float:
    """
    Total Daily Energy Expenditure (суточный расход с учётом активности).

        TDEE = BMR × multiplier(activity_level)

    Args:
        bmr: базальный метаболизм, ккал/сутки.
        activity_level: "low" | "medium" | "high".

    Returns:
        TDEE в ккал/сутки.

    Raises:
        ValueError: некорректный activity_level или bmr <= 0.
    """
    if bmr <= 0:
        raise ValueError(f"bmr must be > 0, got {bmr}")
    if activity_level not in ACTIVITY_MULTIPLIER:
        raise ValueError(
            f"activity_level must be one of {list(ACTIVITY_MULTIPLIER)}, got {activity_level!r}"
        )

    return bmr * ACTIVITY_MULTIPLIER[activity_level]


# -----------------------------------------------------------------
# Targets — дневные нормы под цель
# -----------------------------------------------------------------
def calculate_targets(
    tdee: float,
    weight_kg: float,
    goal: Goal,
) -> NutritionTargets:
    """
    Рассчитать дневные нормы КБЖУ под цель.

    Алгоритм:
        calories = TDEE × goal_multiplier
        protein  = weight × protein_per_kg(goal)
        fat      = weight × 0.9
        carbs    = (calories − protein×4 − fat×9) / 4

    Углеводы — остаток, может быть 0 (если профицит от жиров+белков
    уже превысил цель — такое редко, но возможно на агрессивной сушке).
    В таком случае возвращаем 0 (не отрицательное).

    Args:
        tdee: суточный расход ккал.
        weight_kg: вес тела в кг.
        goal: "bulk" | "maintain" | "cut".

    Returns:
        dict с keys: calories, protein, carbs, fat (все int, граммы или ккал).

    Raises:
        ValueError: некорректный goal или числовые значения <= 0.
    """
    if tdee <= 0:
        raise ValueError(f"tdee must be > 0, got {tdee}")
    if weight_kg <= 0:
        raise ValueError(f"weight_kg must be > 0, got {weight_kg}")
    if goal not in GOAL_CALORIE_MULTIPLIER:
        raise ValueError(
            f"goal must be one of {list(GOAL_CALORIE_MULTIPLIER)}, got {goal!r}"
        )

    calories = int(round(tdee * GOAL_CALORIE_MULTIPLIER[goal]))
    protein_g = int(round(weight_kg * GOAL_PROTEIN_PER_KG[goal]))
    fat_g = int(round(weight_kg * FAT_PER_KG))

    # Остаток калорий → углеводы.
    carbs_kcal = calories - protein_g * KCAL_PER_G_PROTEIN - fat_g * KCAL_PER_G_FAT
    carbs_g = max(0, int(round(carbs_kcal / KCAL_PER_G_CARBS)))

    return NutritionTargets(
        calories=calories,
        protein=protein_g,
        carbs=carbs_g,
        fat=fat_g,
    )
