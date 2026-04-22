"""
Pydantic-схемы для API.

Разделены по зонам: Auth / Profile / Meals / Foods / Recognize.
Все схемы — Pydantic v2 (BaseModel + Field + field_validator).
"""

from __future__ import annotations

from datetime import date as DateType
from datetime import datetime
from enum import Enum
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


# ===============================================================
# Enums (синхронизированы с БД-колонками)
# ===============================================================
class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"


class Goal(str, Enum):
    BULK = "bulk"
    MAINTAIN = "maintain"
    CUT = "cut"


class ActivityLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class MealType(str, Enum):
    BREAKFAST = "breakfast"
    SNACK_1 = "snack_1"
    LUNCH = "lunch"
    SNACK_2 = "snack_2"
    PRE_WORKOUT = "pre_workout"
    POST_WORKOUT = "post_workout"
    DINNER = "dinner"
    BEFORE_SLEEP = "before_sleep"


class Subscription(str, Enum):
    FREE = "free"
    PRO = "pro"
    PRO_PLUS = "pro_plus"


class FoodSource(str, Enum):
    USDA = "usda"
    OFF = "off"
    CUSTOM = "custom"
    SUPPLEMENT = "supplement"


class MealSource(str, Enum):
    PHOTO = "photo"
    SEARCH = "search"
    VOICE = "voice"


# ===============================================================
# Общий базовый класс (pydantic v2 config)
# ===============================================================
class _Base(BaseModel):
    """Общий ConfigDict для всех схем."""

    model_config = ConfigDict(
        from_attributes=True,     # поддержка ORM-like объектов
        str_strip_whitespace=True,
        populate_by_name=True,
        extra="forbid",           # строгая валидация — не пропускаем лишние поля
    )


# ===============================================================
# Auth
# ===============================================================
class RegisterRequest(_Base):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=72)  # bcrypt cap = 72


class LoginRequest(_Base):
    email: EmailStr
    password: str = Field(..., min_length=1, max_length=72)


class RefreshRequest(_Base):
    refresh_token: str = Field(..., min_length=10)


class AuthTokenResponse(_Base):
    access_token: str
    refresh_token: str
    token_type: Literal["bearer"] = "bearer"
    expires_in: int = Field(..., description="TTL access-токена в секундах")


class UserPublic(_Base):
    id: UUID
    email: EmailStr
    subscription: Subscription = Subscription.FREE
    created_at: datetime


# ===============================================================
# Profile
# ===============================================================
class ProfileUpsertRequest(_Base):
    """Используется и для create, и для update (upsert)."""

    gender: Gender
    age: int = Field(..., ge=14, le=100)
    height_cm: int = Field(..., ge=120, le=230)
    weight_kg: float = Field(..., ge=30.0, le=300.0)
    body_fat_pct: float | None = Field(default=None, ge=3.0, le=60.0)
    goal: Goal
    activity_level: ActivityLevel
    supplements: list[str] = Field(
        default_factory=list,
        description="Список кодов: 'whey', 'casein', 'creatine', 'bcaa', 'gainer', 'pre_workout'",
    )

    @field_validator("supplements")
    @classmethod
    def _normalize_supplements(cls, value: list[str]) -> list[str]:
        """Чистим регистр и дубликаты."""
        return sorted({s.lower().strip() for s in value if s.strip()})


class ProfileResponse(_Base):
    id: UUID
    user_id: UUID
    gender: Gender
    age: int
    height_cm: int
    weight_kg: float
    body_fat_pct: float | None = None
    goal: Goal
    activity_level: ActivityLevel

    # Рассчитанные на бэке — target КБЖУ
    tdee: int
    target_kcal: int
    target_protein: int
    target_carbs: int
    target_fat: int

    supplements: list[str] = Field(default_factory=list)
    updated_at: datetime


# ===============================================================
# Foods (справочник)
# ===============================================================
class FoodShort(_Base):
    """Краткая карточка продукта — для списков и вложений в meal."""

    id: UUID
    name_ru: str
    name_en: str | None = None
    source: FoodSource
    kcal_100g: float
    protein_100g: float
    carbs_100g: float
    fat_100g: float


# ===============================================================
# Meals
# ===============================================================
class MealCreate(_Base):
    food_id: UUID
    grams: float = Field(..., gt=0, le=2000)
    meal_type: MealType
    date: DateType = Field(..., description="Дата приёма (YYYY-MM-DD)")
    consumed_at: datetime | None = Field(
        default=None,
        description="Точное время — если не задано, берём now() на бэке",
    )
    source: MealSource = MealSource.SEARCH
    photo_url: str | None = None


class MealUpdate(_Base):
    """Partial update — все поля опциональны."""

    grams: float | None = Field(default=None, gt=0, le=2000)
    meal_type: MealType | None = None
    consumed_at: datetime | None = None


class MealResponse(_Base):
    id: UUID
    user_id: UUID
    date: DateType
    meal_type: MealType
    grams: float

    # Рассчитываются на бэке: grams × food.*_per_100g / 100
    kcal: float
    protein: float
    carbs: float
    fat: float

    food: FoodShort
    source: MealSource
    photo_url: str | None = None
    created_at: datetime


# ===============================================================
# Recognition
# ===============================================================
class RecognizedItem(_Base):
    """Один распознанный продукт."""

    name: str
    grams: float = Field(..., gt=0, le=2000)
    kcal: float = Field(..., ge=0)
    protein: float = Field(..., ge=0)
    carbs: float = Field(..., ge=0)
    fat: float = Field(..., ge=0)
    confidence: float = Field(..., ge=0.0, le=1.0)
    food_id: UUID | None = Field(
        default=None,
        description="id из foods — если продукт удалось смапить",
    )


class RecognizeResponse(_Base):
    """Ответ распознавания фото."""

    model_used: Literal["yolo", "gemini", "yolo+gemini", "cache"]
    items: list[RecognizedItem]
    processing_ms: int = Field(..., ge=0, description="Время обработки, мс")
    photo_url: str | None = Field(
        default=None,
        description="URL фото в Supabase Storage (private bucket)",
    )
