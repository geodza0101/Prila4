# GymFuel AI — Главный пользовательский флоу

**Проект:** AI-счётчик калорий и спортпита для качков
**Форм-фактор:** PWA (mobile-first)
**Документ:** карта навигации MVP

---

## 1. End-to-end флоу (новый пользователь → запись приёма пищи)

```mermaid
flowchart TD
    Start([Пользователь открывает PWA]) --> Splash[Splash / Login]

    Splash -->|Войти через Google/Apple/Email| Auth{Есть аккаунт?}
    Auth -->|Нет| OB1[Онбординг шаг 1:<br/>Пол и возраст]
    Auth -->|Да| Dashboard

    OB1 --> OB2[Шаг 2:<br/>Рост и вес]
    OB2 --> OB3[Шаг 3:<br/>Цель: масса / сушка / поддержка]
    OB3 --> OB4[Шаг 4:<br/>Уровень активности]
    OB4 --> OB5[Шаг 5:<br/>Спортпит на полке]
    OB5 --> Calc[/🔥 Расчёт норм.../]
    Calc --> Norms[Твои нормы:<br/>Ккал · Б · У · Ж]
    Norms -->|Поехали| Dashboard

    Dashboard[🏠 Dashboard<br/>метрики дня + приёмы]

    Dashboard -->|Tap FAB +| ActionSheet{Как записать?}
    Dashboard -->|Tab 'Фото'| PhotoSource
    Dashboard -->|Tab 'Дневник'| MealLog
    Dashboard -->|Tab 'Спортпит'| Supplements
    Dashboard -->|Tab 'Я'| Profile

    ActionSheet -->|📸 Фото| PhotoSource
    ActionSheet -->|🔍 Поиск| Search
    ActionSheet -->|🎤 Голос| Voice[/disabled: Скоро/]

    PhotoSource{Источник фото}
    PhotoSource -->|Снять сейчас| Camera[📸 Камера / захват]
    PhotoSource -->|Из галереи| Picker[Выбор из галереи]

    Camera --> Preview[Preview фото]
    Picker --> Preview
    Preview -->|Переснять| PhotoSource
    Preview -->|✨ Распознать| Loading[/Распознаю.../<br/>scan-animation 3-5s]

    Loading -->|success| Result[Результаты:<br/>список продуктов + КБЖУ]
    Loading -->|fail| RecogError[❌ Не получилось.<br/>Переснять / Ввести руками]
    RecogError -->|Переснять| PhotoSource
    RecogError -->|Руками| Search

    Result -->|Редактировать граммы| Result
    Result -->|+ Добавить вручную| Search
    Result -->|Выбрать приём: Завтрак/Обед/...| Result
    Result -->|Записать в дневник| Save[/Сохранение/]
    Save --> Toast[✓ Записано в Обед]
    Toast --> Dashboard

    Search[🔍 Поиск продукта<br/>autocomplete + избранное]
    Search -->|Выбрать продукт| EditGrams[Граммовка + приём пищи]
    EditGrams -->|Записать| Save

    MealLog[📖 Meal Log<br/>все приёмы за день]
    MealLog -->|Свайп по дням| MealLog
    MealLog -->|Tap на приём| EditMeal[Редактировать приём]
    MealLog -->|FAB +| ActionSheet
    EditMeal --> MealLog

    Supplements[💊 Спортпит<br/>На полке / Рекомендации]
    Supplements -->|Принял| Save
    Supplements -->|+ Добавить| AddSupp[Выбор добавки]
    AddSupp --> Supplements

    Profile[👤 Профиль]
    Profile -->|Пересчитать нормы| OB3

    classDef primary fill:#FF6B00,stroke:#FF6B00,color:#0F0F10,font-weight:bold
    classDef screen fill:#1A1A1C,stroke:#2A2A2E,color:#FFFFFF
    classDef success fill:#6BCB77,stroke:#6BCB77,color:#0F0F10
    classDef error fill:#E5484D,stroke:#E5484D,color:#FFFFFF
    classDef process fill:#242428,stroke:#2A2A2E,color:#B8B8BE,font-style:italic

    class Start,Splash primary
    class OB1,OB2,OB3,OB4,OB5,Dashboard,PhotoSource,Camera,Picker,Preview,Result,Search,EditGrams,MealLog,EditMeal,Supplements,AddSupp,Profile,Norms screen
    class Toast success
    class RecogError error
    class Calc,Loading,Save,Voice process
```

---

## 2. Ключевой happy-path (3 тапа до записи)

```mermaid
sequenceDiagram
    actor U as Качок
    participant D as Dashboard
    participant C as Camera
    participant AI as AI-recognizer
    participant L as Meal Log

    U->>D: Открывает app
    Note over D: Видит 1842 / 2400 ккал
    U->>D: Tap FAB (+) → Фото
    D->>C: Открыть камеру
    U->>C: Снимает тарелку
    C->>AI: POST /recognize (image)
    Note over AI: scan-animation<br/>3-5 секунд
    AI-->>C: [Курица 200г, Рис 150г, Масло 10г]
    C->>U: Показать результаты + редактор
    U->>C: Принимает (Записать в дневник)
    C->>L: POST /meals
    L-->>D: Обновить прогресс
    D->>U: Toast "✓ Записано в Обед"
    Note over D: 1842 → 2140 ккал<br/>(count-up анимация)
```

---

## 3. Состояния экранов (error / empty / loading)

```mermaid
stateDiagram-v2
    [*] --> Dashboard

    state Dashboard {
        [*] --> DashLoading
        DashLoading --> DashEmpty: первый день
        DashLoading --> DashFilled: есть записи
        DashLoading --> DashError: нет сети
        DashError --> DashLoading: retry
    }

    state PhotoFlow {
        [*] --> SourceSelect
        SourceSelect --> CapturePreview: снято
        CapturePreview --> Recognizing: Распознать
        Recognizing --> Results: success
        Recognizing --> RecogFailed: fail
        Recognizing --> NoMatch: не найдено
        RecogFailed --> SourceSelect: Переснять
        NoMatch --> ManualEntry: Ввести вручную
        Results --> Saved: Записать
        Saved --> [*]
    }

    Dashboard --> PhotoFlow: + Фото
    PhotoFlow --> Dashboard: после сохранения
```

---

## 4. Навигационная иерархия (5 табов)

```mermaid
graph LR
    Root[GymFuel AI] --> Tab1[🏠 Дом<br/>Dashboard]
    Root --> Tab2[📖 Дневник<br/>Meal Log]
    Root --> Tab3[📷 Фото<br/>центральный CTA]
    Root --> Tab4[💊 Спортпит<br/>Supplements]
    Root --> Tab5[👤 Я<br/>Profile]

    Tab1 --> Tab1a[Quick Actions]
    Tab1 --> Tab1b[Сегодняшние приёмы]
    Tab1 --> Tab1c[Спортпит на сегодня]

    Tab2 --> Tab2a[Приёмы по дням]
    Tab2 --> Tab2b[Поиск продукта]

    Tab3 --> Tab3a[Preview]
    Tab3a --> Tab3b[Распознавание]
    Tab3b --> Tab3c[Редактор граммовки]

    Tab4 --> Tab4a[На полке]
    Tab4 --> Tab4b[Рекомендации]
    Tab4 --> Tab4c[Каталог]

    Tab5 --> Tab5a[Мои нормы]
    Tab5 --> Tab5b[Параметры]
    Tab5 --> Tab5c[Подписка]
    Tab5 --> Tab5d[Настройки]

    classDef tab fill:#FF6B00,stroke:#FF6B00,color:#0F0F10,font-weight:bold
    classDef sub fill:#1A1A1C,stroke:#2A2A2E,color:#FFFFFF
    class Tab1,Tab2,Tab3,Tab4,Tab5 tab
    class Tab1a,Tab1b,Tab1c,Tab2a,Tab2b,Tab3a,Tab3b,Tab3c,Tab4a,Tab4b,Tab4c,Tab5a,Tab5b,Tab5c,Tab5d sub
```

---

## 5. Метрики флоу (целевые)

| Путь | Тапов | Время | Приоритет |
|------|-------|-------|-----------|
| Onboarding (новый юзер) | 6 | ~90 сек | High |
| Dashboard → Фото → Записать | **3** | ~8 сек | **CRITICAL** |
| Dashboard → Поиск → Записать | 4 | ~15 сек | High |
| Dashboard → Спортпит → Принял | 3 | ~5 сек | Medium |
| Профиль → Пересчитать нормы | 3 | ~20 сек | Low |

**Главный KPI UX:** Dashboard → запись приёма пищи ≤ 3 тапа (см. Design Principle P3 из ТЗ).

---

## Связанные документы
- `03_ТЗ_дизайн_приложения.md` — полная спецификация экранов (раздел 5–6)
- `Dashboard.tsx` — React-реализация главного экрана
- `PhotoRecognition.tsx` — три состояния флоу распознавания
- `preview.html` — статичный визуальный референс Dashboard
