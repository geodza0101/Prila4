# 🏢 Многоагентная система GymFuel AI

**Проект:** AI-счётчик калорий для качков
**Дата:** 2026-04-21
**Всего агентов:** 14 (5 маркетинг + 7 разработка + 2 связующих)

---

## 📁 Структура папок

```
Агенты/
├── README.md (этот файл)
├── Маркетинг/
│   ├── cmo-orchestrator.md      ⭐ Глава маркетинга
│   ├── market-researcher.md     🔎 Исследование рынка и ЦА
│   ├── copywriter.md            ✍️ Тексты, лендинги, посты
│   ├── content-producer.md      🎬 Reels, сценарии, прогрев
│   └── community-manager.md     💬 Чат, комментарии, отзывы
├── Разработка/
│   ├── cto-orchestrator.md      ⭐ Глава разработки
│   ├── product-manager.md       📋 User stories, acceptance
│   ├── backend-dev.md           🔧 FastAPI + Supabase
│   ├── frontend-dev.md          🖥️ Next.js + shadcn/ui
│   ├── ai-engineer.md           🧠 YOLOv8 + Gemini/Claude
│   ├── qa-engineer.md           🧪 Тесты + регрессия
│   └── devops.md                ⚙️ Деплой, CI/CD, мониторинг
└── Связующие/
    ├── product-owner-assistant.md  👔 Помощник PO (Георгий)
    └── analyst.md                  📊 Метрики, дашборды
```

---

## 🎯 Как использовать

Эти файлы — **черновики агентов** под проект GymFuel AI. Чтобы они начали работать в Claude Code:

**Вариант 1 (локально — только для этого проекта):**
```bash
mkdir -p "/Users/geodza/Desktop/Урок 11/.claude/agents"
cp Агенты/Маркетинг/*.md "/Users/geodza/Desktop/Урок 11/.claude/agents/"
cp Агенты/Разработка/*.md "/Users/geodza/Desktop/Урок 11/.claude/agents/"
cp Агенты/Связующие/*.md "/Users/geodza/Desktop/Урок 11/.claude/agents/"
```

**Вариант 2 (глобально — для всех проектов):**
```bash
cp Агенты/Маркетинг/*.md ~/.claude/agents/
# и т.д.
```

После копирования Claude Code автоматически подхватит агентов при следующем запуске.

---

## 🔄 Workflow взаимодействия

```
Георгий (PO) → cmo-orchestrator ──┬── market-researcher
                                  ├── copywriter
                                  ├── content-producer
                                  └── community-manager

Георгий (PO) → cto-orchestrator ──┬── product-manager
                                  ├── backend-dev
                                  ├── frontend-dev
                                  ├── ai-engineer
                                  ├── qa-engineer
                                  └── devops

Все отделы → analyst → отчёт Георгию
product-owner-assistant ← работает с Георгием напрямую
```

---

## 📊 Сводная таблица

### Маркетинг (5)
| Агент | Модель | Основная задача |
|-------|--------|-----------------|
| cmo-orchestrator | opus | Распределяет задачи, ставит KPI |
| market-researcher | haiku | Сбор данных о рынке и ЦА |
| copywriter | sonnet | Тексты, лендинги, посты |
| content-producer | sonnet | Контент-план, reels |
| community-manager | haiku | Отзывы, вопросы пользователей |

### Разработка (7)
| Агент | Модель | Основная задача |
|-------|--------|-----------------|
| cto-orchestrator | opus | Спринты, приоритизация |
| product-manager | sonnet | User stories, acceptance |
| backend-dev | sonnet | FastAPI, Supabase, API |
| frontend-dev | sonnet | Next.js, UI |
| ai-engineer | opus | AI/ML модели |
| qa-engineer | sonnet | Тесты, регрессия |
| devops | sonnet | Деплой, CI/CD |

### Связующие (2)
| Агент | Модель | Основная задача |
|-------|--------|-----------------|
| product-owner-assistant | sonnet | Помощник Георгия |
| analyst | sonnet | Метрики, дашборды |

---

## 📎 Связанные файлы проекта

- [Идея.md](../Идея.md) — продуктовая концепция
- [Техническое задание.md](../Техническое%20задание.md) — функциональное ТЗ
- [Требование к дизайну.md](../Требование%20к%20дизайну.md) — дизайн-спецификация
- [Задачник.md](../Задачник.md) — прогресс проекта

**Все агенты ОБЯЗАНЫ читать эти файлы для контекста.**
