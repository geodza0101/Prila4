-- ================================================================
-- GymFuel AI — Initial Schema
-- Migration: 0001_initial_schema.sql
-- Source:    Техническое задание.md, раздел 5 (Модель данных)
-- Target:    Supabase (PostgreSQL 15 + pgvector + auth.*)
-- ================================================================
-- Применение:
--   supabase db push
--   -- или вручную через Supabase SQL Editor
-- ================================================================

-- ----------------------------------------------------------------
-- Extensions
-- ----------------------------------------------------------------
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS vector;     -- pgvector — для embeddings в foods
CREATE EXTENSION IF NOT EXISTS pgcrypto;


-- ================================================================
-- ENUM types — вместо TEXT CHECK — для типобезопасности на уровне БД
-- ================================================================
DO $$ BEGIN
    CREATE TYPE subscription_tier AS ENUM ('free', 'pro', 'pro_plus');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE gender_type AS ENUM ('male', 'female');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE goal_type AS ENUM ('bulk', 'maintain', 'cut');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE activity_type AS ENUM ('low', 'medium', 'high');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE meal_type AS ENUM (
        'breakfast', 'snack_1', 'lunch', 'snack_2',
        'pre_workout', 'post_workout', 'dinner', 'before_sleep'
    );
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE food_source AS ENUM ('usda', 'off', 'custom', 'supplement');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE meal_source AS ENUM ('photo', 'search', 'voice');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE chat_role AS ENUM ('user', 'assistant', 'system');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;


-- ================================================================
-- TABLE: users
-- Расширение Supabase Auth (auth.users).
-- ================================================================
CREATE TABLE IF NOT EXISTS public.users (
    id            UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email         TEXT NOT NULL UNIQUE,
    subscription  subscription_tier NOT NULL DEFAULT 'free',
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

COMMENT ON TABLE public.users IS 'Бизнес-профиль поверх auth.users (subscription и т.д.)';


-- ================================================================
-- TABLE: profiles
-- ================================================================
CREATE TABLE IF NOT EXISTS public.profiles (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id         UUID NOT NULL UNIQUE REFERENCES public.users(id) ON DELETE CASCADE,

    -- Персональные параметры
    gender          gender_type NOT NULL,
    age             INT NOT NULL CHECK (age BETWEEN 14 AND 100),
    height_cm       INT NOT NULL CHECK (height_cm BETWEEN 120 AND 230),
    weight_kg       NUMERIC(5, 2) NOT NULL CHECK (weight_kg BETWEEN 30 AND 300),
    body_fat_pct    NUMERIC(4, 2) CHECK (body_fat_pct BETWEEN 3 AND 60),

    -- Цели и активность
    goal            goal_type NOT NULL,
    activity_level  activity_type NOT NULL,

    -- Рассчитанные нормы КБЖУ (обновляются бэком на upsert/recalculate)
    tdee            INT NOT NULL,
    target_kcal     INT NOT NULL,
    target_protein  INT NOT NULL,
    target_carbs    INT NOT NULL,
    target_fat      INT NOT NULL,

    -- Спортпит — массив кодов: ['whey', 'creatine', 'bcaa']
    supplements     JSONB NOT NULL DEFAULT '[]'::jsonb,

    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_profiles_user_id ON public.profiles(user_id);

COMMENT ON COLUMN public.profiles.supplements IS
    'JSON-массив кодов: whey, casein, creatine, bcaa, gainer, pre_workout';


-- ================================================================
-- TABLE: foods — справочник продуктов (USDA / OFF / custom / supplement)
-- ================================================================
CREATE TABLE IF NOT EXISTS public.foods (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    external_id     TEXT,                          -- id из USDA (fdcId) или OFF (barcode)
    source          food_source NOT NULL,
    name_ru         TEXT NOT NULL,
    name_en         TEXT,

    kcal_100g       NUMERIC(7, 2) NOT NULL CHECK (kcal_100g >= 0),
    protein_100g    NUMERIC(6, 2) NOT NULL CHECK (protein_100g >= 0),
    carbs_100g      NUMERIC(6, 2) NOT NULL CHECK (carbs_100g >= 0),
    fat_100g        NUMERIC(6, 2) NOT NULL CHECK (fat_100g >= 0),

    -- Embedding для семантического поиска (всё равно ведём pgvector)
    -- 384 — размерность sentence-transformers/all-MiniLM-L6-v2
    embedding       VECTOR(384),

    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),

    -- Дедупликация по (source, external_id)
    UNIQUE (source, external_id)
);

-- Триграм-индекс для быстрого подстрочного поиска по названию (автокомплит)
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE INDEX IF NOT EXISTS idx_foods_name_ru_trgm ON public.foods USING gin (name_ru gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_foods_name_en_trgm ON public.foods USING gin (name_en gin_trgm_ops);

-- HNSW-индекс для pgvector (быстрый ANN-поиск)
CREATE INDEX IF NOT EXISTS idx_foods_embedding_hnsw
    ON public.foods
    USING hnsw (embedding vector_cosine_ops);


-- ================================================================
-- TABLE: meals — дневник питания
-- ================================================================
CREATE TABLE IF NOT EXISTS public.meals (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id         UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    date            DATE NOT NULL,
    meal_type       meal_type NOT NULL,
    food_id         UUID NOT NULL REFERENCES public.foods(id) ON DELETE RESTRICT,
    grams           NUMERIC(7, 2) NOT NULL CHECK (grams > 0 AND grams <= 2000),

    -- Посчитано на бэке: grams × food.*_per_100g / 100
    kcal            NUMERIC(8, 2) NOT NULL CHECK (kcal >= 0),
    protein         NUMERIC(7, 2) NOT NULL CHECK (protein >= 0),
    carbs           NUMERIC(7, 2) NOT NULL CHECK (carbs >= 0),
    fat             NUMERIC(7, 2) NOT NULL CHECK (fat >= 0),

    photo_url       TEXT,                         -- ссылка в Supabase Storage (private bucket)
    source          meal_source NOT NULL DEFAULT 'search',

    consumed_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_meals_user_date ON public.meals(user_id, date DESC);
CREATE INDEX IF NOT EXISTS idx_meals_food_id ON public.meals(food_id);


-- ================================================================
-- TABLE: supplements_stock — что у пользователя на полке
-- ================================================================
CREATE TABLE IF NOT EXISTS public.supplements_stock (
    id                    UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id               UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    supplement_type       TEXT NOT NULL,          -- 'whey' | 'creatine' | 'bcaa' | ...
    brand                 TEXT,
    serving_size_g        NUMERIC(6, 2) NOT NULL CHECK (serving_size_g > 0),
    protein_per_serving   NUMERIC(6, 2) NOT NULL CHECK (protein_per_serving >= 0),
    kcal_per_serving      NUMERIC(6, 2) NOT NULL CHECK (kcal_per_serving >= 0),
    servings_left         INT NOT NULL DEFAULT 0 CHECK (servings_left >= 0),
    added_at              TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_supplements_stock_user ON public.supplements_stock(user_id);


-- ================================================================
-- TABLE: weight_logs
-- ================================================================
CREATE TABLE IF NOT EXISTS public.weight_logs (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id     UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    weight_kg   NUMERIC(5, 2) NOT NULL CHECK (weight_kg BETWEEN 30 AND 300),
    logged_at   DATE NOT NULL DEFAULT CURRENT_DATE,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),

    -- Один замер в день на пользователя (если нужно несколько — убрать UNIQUE)
    UNIQUE (user_id, logged_at)
);

CREATE INDEX IF NOT EXISTS idx_weight_logs_user_date
    ON public.weight_logs(user_id, logged_at DESC);


-- ================================================================
-- TABLE: chat_messages (для AI-диетолога, v1.0)
-- ================================================================
CREATE TABLE IF NOT EXISTS public.chat_messages (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id     UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    role        chat_role NOT NULL,
    content     TEXT NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_chat_messages_user_time
    ON public.chat_messages(user_id, created_at DESC);


-- ================================================================
-- Trigger: автообновление updated_at
-- ================================================================
CREATE OR REPLACE FUNCTION public.set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_users_updated_at ON public.users;
CREATE TRIGGER trg_users_updated_at
    BEFORE UPDATE ON public.users
    FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();

DROP TRIGGER IF EXISTS trg_profiles_updated_at ON public.profiles;
CREATE TRIGGER trg_profiles_updated_at
    BEFORE UPDATE ON public.profiles
    FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();


-- ================================================================
-- ROW-LEVEL SECURITY (RLS)
-- Принцип: пользователь видит ТОЛЬКО свои данные (auth.uid() = user_id).
-- Foods — публичные (read-all), запись — только service_role.
-- ================================================================

-- ---- users ----------------------------------------------------
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS users_select_own ON public.users;
CREATE POLICY users_select_own ON public.users
    FOR SELECT USING (auth.uid() = id);

DROP POLICY IF EXISTS users_update_own ON public.users;
CREATE POLICY users_update_own ON public.users
    FOR UPDATE USING (auth.uid() = id);

-- ---- profiles -------------------------------------------------
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS profiles_all_own ON public.profiles;
CREATE POLICY profiles_all_own ON public.profiles
    FOR ALL USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

-- ---- foods (публичный каталог) --------------------------------
ALTER TABLE public.foods ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS foods_select_all ON public.foods;
CREATE POLICY foods_select_all ON public.foods
    FOR SELECT USING (true);
-- Запись в foods — только сервисным ключом (обходит RLS); отдельной INSERT-policy нет.

-- ---- meals ----------------------------------------------------
ALTER TABLE public.meals ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS meals_all_own ON public.meals;
CREATE POLICY meals_all_own ON public.meals
    FOR ALL USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

-- ---- supplements_stock ---------------------------------------
ALTER TABLE public.supplements_stock ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS supplements_all_own ON public.supplements_stock;
CREATE POLICY supplements_all_own ON public.supplements_stock
    FOR ALL USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

-- ---- weight_logs ---------------------------------------------
ALTER TABLE public.weight_logs ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS weight_logs_all_own ON public.weight_logs;
CREATE POLICY weight_logs_all_own ON public.weight_logs
    FOR ALL USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

-- ---- chat_messages -------------------------------------------
ALTER TABLE public.chat_messages ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS chat_all_own ON public.chat_messages;
CREATE POLICY chat_all_own ON public.chat_messages
    FOR ALL USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);


-- ================================================================
-- Seed: минимальный набор спортпита (source='supplement')
-- Из ТЗ 2.3.1 — Whey / Casein / Creatine / BCAA / Gainer / Pre-workout
-- ================================================================
INSERT INTO public.foods (source, name_ru, name_en, kcal_100g, protein_100g, carbs_100g, fat_100g)
VALUES
    ('supplement', 'Сывороточный протеин (Whey)', 'Whey Protein', 400, 80, 8, 5),
    ('supplement', 'Казеин',                      'Casein',       380, 75, 6, 3),
    ('supplement', 'Креатин моногидрат',          'Creatine Monohydrate', 0, 0, 0, 0),
    ('supplement', 'BCAA',                        'BCAA',         380, 90, 0, 0),
    ('supplement', 'Гейнер',                      'Mass Gainer',  380, 25, 60, 3),
    ('supplement', 'Пред-тренировочник',          'Pre-Workout',  100, 0, 20, 0)
ON CONFLICT (source, external_id) DO NOTHING;
