"""
Unit-тесты для app.services.nutrition.

Значения BMR/TDEE сверены с:
- Mifflin-St Jeor (оригинал 1990) — референсные калькуляторы
  (например: https://www.calculator.net/bmr-calculator.html).
- ISSN Position Stand on protein intake (Jäger et al., 2017).

Принцип: тесты называют ЯВНО кого считаем
(мужчина 25, 80 кг, 180 см, medium) — чтобы при изменении формул
было видно на каком профиле регресс.
"""

from __future__ import annotations

import pytest

from app.services.nutrition import (
    ACTIVITY_MULTIPLIER,
    FAT_PER_KG,
    GOAL_CALORIE_MULTIPLIER,
    GOAL_PROTEIN_PER_KG,
    calculate_bmr,
    calculate_targets,
    calculate_tdee,
)


# =================================================================
# BMR — Mifflin-St Jeor
# =================================================================
class TestCalculateBMR:
    def test_male_reference_profile(self) -> None:
        """
        Мужчина 25 лет, 80 кг, 180 см.

        BMR = 10*80 + 6.25*180 − 5*25 + 5 = 800 + 1125 − 125 + 5 = 1805
        """
        assert calculate_bmr(weight_kg=80, height_cm=180, age=25, gender="male") == pytest.approx(
            1805.0
        )

    def test_female_reference_profile(self) -> None:
        """
        Женщина 30 лет, 60 кг, 165 см.

        BMR = 10*60 + 6.25*165 − 5*30 − 161 = 600 + 1031.25 − 150 − 161 = 1320.25
        """
        assert calculate_bmr(
            weight_kg=60, height_cm=165, age=30, gender="female"
        ) == pytest.approx(1320.25)

    def test_young_male(self) -> None:
        """Мужчина 18 лет, 70 кг, 175 см — молодой атлет."""
        # 10*70 + 6.25*175 − 5*18 + 5 = 700 + 1093.75 − 90 + 5 = 1708.75
        assert calculate_bmr(
            weight_kg=70, height_cm=175, age=18, gender="male"
        ) == pytest.approx(1708.75)

    def test_older_female(self) -> None:
        """Женщина 55 лет, 70 кг, 160 см."""
        # 10*70 + 6.25*160 − 5*55 − 161 = 700 + 1000 − 275 − 161 = 1264
        assert calculate_bmr(
            weight_kg=70, height_cm=160, age=55, gender="female"
        ) == pytest.approx(1264.0)

    def test_male_vs_female_difference_is_166(self) -> None:
        """
        Разница BMR между мужчиной и женщиной с одинаковыми параметрами
        по формуле = (+5) − (−161) = 166 ккал.
        """
        bmr_m = calculate_bmr(weight_kg=70, height_cm=170, age=30, gender="male")
        bmr_f = calculate_bmr(weight_kg=70, height_cm=170, age=30, gender="female")
        assert bmr_m - bmr_f == pytest.approx(166.0)

    @pytest.mark.parametrize(
        "kw",
        [
            {"weight_kg": 0, "height_cm": 180, "age": 25, "gender": "male"},
            {"weight_kg": 80, "height_cm": -1, "age": 25, "gender": "male"},
            {"weight_kg": 80, "height_cm": 180, "age": -5, "gender": "male"},
            {"weight_kg": 80, "height_cm": 180, "age": 25, "gender": "other"},
        ],
    )
    def test_invalid_inputs_raise(self, kw: dict) -> None:
        with pytest.raises(ValueError):
            calculate_bmr(**kw)


# =================================================================
# TDEE
# =================================================================
class TestCalculateTDEE:
    def test_medium_activity(self) -> None:
        """BMR 1805, activity=medium (×1.55) → 2797.75"""
        assert calculate_tdee(bmr=1805.0, activity_level="medium") == pytest.approx(2797.75)

    def test_low_activity(self) -> None:
        """BMR 1800, activity=low (×1.375) → 2475"""
        assert calculate_tdee(bmr=1800.0, activity_level="low") == pytest.approx(2475.0)

    def test_high_activity(self) -> None:
        """BMR 2000, activity=high (×1.725) → 3450"""
        assert calculate_tdee(bmr=2000.0, activity_level="high") == pytest.approx(3450.0)

    def test_multipliers_are_monotonic(self) -> None:
        """low < medium < high — здравый смысл."""
        assert ACTIVITY_MULTIPLIER["low"] < ACTIVITY_MULTIPLIER["medium"]
        assert ACTIVITY_MULTIPLIER["medium"] < ACTIVITY_MULTIPLIER["high"]

    def test_invalid_activity_raises(self) -> None:
        with pytest.raises(ValueError):
            calculate_tdee(bmr=1800.0, activity_level="super_high")  # type: ignore[arg-type]

    def test_nonpositive_bmr_raises(self) -> None:
        with pytest.raises(ValueError):
            calculate_tdee(bmr=0.0, activity_level="medium")


# =================================================================
# Targets (КБЖУ)
# =================================================================
class TestCalculateTargets:
    def test_bulk_80kg(self) -> None:
        """
        Массонабор для 80 кг, TDEE=2800:
          calories = 2800 × 1.15 = 3220
          protein  = 80 × 2.0 = 160 г → 640 ккал
          fat      = 80 × 0.9 = 72 г  → 648 ккал
          carbs    = (3220 − 640 − 648) / 4 = 1932 / 4 = 483 г
        """
        t = calculate_targets(tdee=2800.0, weight_kg=80.0, goal="bulk")
        assert t["calories"] == 3220
        assert t["protein"] == 160
        assert t["fat"] == 72
        assert t["carbs"] == 483

    def test_cut_80kg(self) -> None:
        """
        Сушка для 80 кг, TDEE=2800:
          calories = 2800 × 0.80 = 2240
          protein  = 80 × 2.3 = 184 г → 736 ккал
          fat      = 80 × 0.9 = 72 г  → 648 ккал
          carbs    = (2240 − 736 − 648) / 4 = 856 / 4 = 214 г
        """
        t = calculate_targets(tdee=2800.0, weight_kg=80.0, goal="cut")
        assert t["calories"] == 2240
        assert t["protein"] == 184
        assert t["fat"] == 72
        assert t["carbs"] == 214

    def test_maintain_70kg(self) -> None:
        """
        Поддержка для 70 кг, TDEE=2500:
          calories = 2500
          protein  = 70 × 1.8 = 126 г → 504 ккал
          fat      = 70 × 0.9 = 63 г  → 567 ккал
          carbs    = (2500 − 504 − 567) / 4 = 1429 / 4 = 357.25 → 357
        """
        t = calculate_targets(tdee=2500.0, weight_kg=70.0, goal="maintain")
        assert t["calories"] == 2500
        assert t["protein"] == 126
        assert t["fat"] == 63
        assert t["carbs"] == 357

    def test_carbs_never_negative(self) -> None:
        """
        Patho-case: маленький TDEE + крутая сушка —
        белок+жир могут перекрыть калории → carbs должен быть ≥ 0.
        """
        # TDEE 1200, cut: calories = 960; protein(80kg×2.3)=184g=736kcal; fat=72g=648kcal
        # остаток: 960 − 736 − 648 = −424 → carbs = max(0, ...) = 0
        t = calculate_targets(tdee=1200.0, weight_kg=80.0, goal="cut")
        assert t["carbs"] == 0
        assert t["protein"] > 0
        assert t["fat"] > 0

    def test_bulk_calories_above_tdee(self) -> None:
        """Массонабор → калорий ВСЕГДА больше чем TDEE."""
        tdee = 2500.0
        t = calculate_targets(tdee=tdee, weight_kg=75.0, goal="bulk")
        assert t["calories"] > tdee

    def test_cut_calories_below_tdee(self) -> None:
        """Сушка → калорий ВСЕГДА меньше чем TDEE."""
        tdee = 2500.0
        t = calculate_targets(tdee=tdee, weight_kg=75.0, goal="cut")
        assert t["calories"] < tdee

    def test_invalid_goal_raises(self) -> None:
        with pytest.raises(ValueError):
            calculate_targets(tdee=2500.0, weight_kg=75.0, goal="starve")  # type: ignore[arg-type]

    def test_constants_sanity(self) -> None:
        """Быстрая проверка, что константы не рассинхрон."""
        assert set(GOAL_CALORIE_MULTIPLIER) == set(GOAL_PROTEIN_PER_KG)
        assert GOAL_CALORIE_MULTIPLIER["bulk"] > 1.0
        assert GOAL_CALORIE_MULTIPLIER["cut"] < 1.0
        assert GOAL_PROTEIN_PER_KG["cut"] > GOAL_PROTEIN_PER_KG["bulk"]  # на сушке белка больше
        assert 0.5 <= FAT_PER_KG <= 1.5


# =================================================================
# Интеграционный сценарий (BMR → TDEE → targets)
# =================================================================
class TestFullScenario:
    def test_full_chain_male_bulk(self) -> None:
        """
        Мужчина 25 лет, 80 кг, 180 см, medium activity, массонабор.

          BMR    = 1805
          TDEE   = 1805 × 1.55 = 2797.75
          calories = 2797.75 × 1.15 ≈ 3217
          protein  = 80 × 2.0 = 160
          fat      = 80 × 0.9 = 72
          carbs    = (3217 − 640 − 648) / 4 = 482.25 → 482
        """
        bmr = calculate_bmr(weight_kg=80, height_cm=180, age=25, gender="male")
        tdee = calculate_tdee(bmr=bmr, activity_level="medium")
        t = calculate_targets(tdee=tdee, weight_kg=80, goal="bulk")

        assert bmr == pytest.approx(1805.0)
        assert tdee == pytest.approx(2797.75)
        assert t["calories"] == 3217
        assert t["protein"] == 160
        assert t["fat"] == 72
        assert t["carbs"] == 482
