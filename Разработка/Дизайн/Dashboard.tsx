"use client";

import * as React from "react";
// shadcn/ui stubs — в реальном проекте заменить на "@/components/ui/*"
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import {
  Bell,
  Home,
  Camera,
  BookOpen,
  Zap,
  User,
  Plus,
  Flame,
  Dumbbell,
  Clock,
  ChevronRight,
} from "lucide-react";

/**
 * GymFuel AI — Dashboard (Home)
 * Design system: Dark-first, #0F0F10 bg, #FF6B00 accent, Inter, 4px grid.
 * Mobile-first (375px). Безопасные Tailwind-классы (inline arbitrary values для точных HEX).
 */

type Macro = {
  key: "calories" | "protein" | "carbs" | "fat";
  label: string;
  unit: string;
  eaten: number;
  goal: number;
  /** Цвет progress — из data viz палитры ТЗ */
  color: string;
};

const MACROS: Macro[] = [
  { key: "calories", label: "Калории", unit: "ккал", eaten: 1842, goal: 2400, color: "#FF6B00" },
  { key: "protein", label: "Белок", unit: "г", eaten: 145, goal: 200, color: "#3B9EFF" },
  { key: "carbs", label: "Углеводы", unit: "г", eaten: 220, goal: 260, color: "#F5C842" },
  { key: "fat", label: "Жиры", unit: "г", eaten: 58, goal: 70, color: "#A371F7" },
];

type Meal = {
  id: string;
  time: string;
  title: string;
  kcal: number;
  p: number;
  c: number;
  f: number;
  items: string[];
};

const MEALS: Meal[] = [
  {
    id: "1",
    time: "08:30",
    title: "Завтрак",
    kcal: 520,
    p: 38,
    c: 62,
    f: 14,
    items: ["Овсянка 80г", "Яйца 3шт", "Банан 120г"],
  },
  {
    id: "2",
    time: "12:15",
    title: "Перекус",
    kcal: 280,
    p: 28,
    c: 30,
    f: 6,
    items: ["Творог 5% 200г", "Мёд 20г"],
  },
  {
    id: "3",
    time: "14:30",
    title: "Обед",
    kcal: 742,
    p: 54,
    c: 90,
    f: 22,
    items: ["Куриная грудка 200г", "Рис басмати 150г", "Оливк. масло 10г"],
  },
  {
    id: "4",
    time: "17:00",
    title: "До трени",
    kcal: 300,
    p: 25,
    c: 38,
    f: 8,
    items: ["Whey 30г", "Бублик 60г"],
  },
];

function pct(eaten: number, goal: number) {
  return Math.min(100, Math.round((eaten / goal) * 100));
}

export default function Dashboard() {
  const [mode, setMode] = React.useState<"training" | "rest">("training");
  const [range, setRange] = React.useState<"day" | "week">("day");

  return (
    <div className="min-h-screen bg-[#0F0F10] text-white font-[Inter,system-ui,-apple-system,sans-serif] antialiased pb-28">
      {/* Header */}
      <header className="sticky top-0 z-30 bg-[#0F0F10]/92 backdrop-blur border-b border-white/[0.06]">
        <div className="mx-auto max-w-md px-4 h-14 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div
              aria-label="Аватар"
              className="h-9 w-9 rounded-full bg-[#FF6B00] text-[#0F0F10] font-bold flex items-center justify-center text-sm"
            >
              Г
            </div>
            <div className="leading-tight">
              <div className="text-[15px] font-semibold">Сегодня</div>
              <div className="text-[13px] text-[#B8B8BE]">22 апр, Ср</div>
            </div>
          </div>

          <div className="flex items-center gap-2">
            {/* Переключатель день/неделя */}
            <div
              role="tablist"
              aria-label="Период"
              className="flex items-center rounded-xl bg-[#1A1A1C] p-1 border border-white/[0.06]"
            >
              <button
                role="tab"
                aria-selected={range === "day"}
                onClick={() => setRange("day")}
                className={`h-8 px-3 text-[12px] font-semibold rounded-lg transition-colors ${
                  range === "day"
                    ? "bg-[#2A2A2E] text-white"
                    : "text-[#B8B8BE] hover:text-white"
                }`}
              >
                День
              </button>
              <button
                role="tab"
                aria-selected={range === "week"}
                onClick={() => setRange("week")}
                className={`h-8 px-3 text-[12px] font-semibold rounded-lg transition-colors ${
                  range === "week"
                    ? "bg-[#2A2A2E] text-white"
                    : "text-[#B8B8BE] hover:text-white"
                }`}
              >
                Неделя
              </button>
            </div>

            <button
              aria-label="Уведомления"
              className="relative h-11 w-11 rounded-full flex items-center justify-center hover:bg-white/[0.04] transition"
            >
              <Bell className="h-5 w-5" strokeWidth={1.75} />
              <span className="absolute top-2 right-2 h-2 w-2 rounded-full bg-[#FF6B00]" />
            </button>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-md px-4 pt-5 space-y-5">
        {/* 4 большие метрики */}
        <section aria-label="Метрики дня">
          <Card className="bg-[#1A1A1C] border border-white/[0.06] rounded-2xl p-5 shadow-[0_2px_6px_rgba(0,0,0,0.35)]">
            {/* Главная метрика — калории */}
            <div className="text-center">
              <div className="text-[13px] text-[#B8B8BE] font-medium uppercase tracking-wider">
                Калории
              </div>
              <div className="mt-1 flex items-baseline justify-center gap-2">
                <span
                  className="text-[56px] leading-none font-extrabold tabular-nums tracking-tight"
                  style={{ fontVariantNumeric: "tabular-nums" }}
                >
                  1 842
                </span>
                <span className="text-[15px] text-[#B8B8BE]">/ 2 400 ккал</span>
              </div>
              <div className="mt-3 h-2 w-full rounded-full bg-[#242428] overflow-hidden">
                <div
                  className="h-full rounded-full transition-[width] duration-500 ease-out"
                  style={{
                    width: `${pct(1842, 2400)}%`,
                    background: "linear-gradient(90deg, #FF6B00 0%, #FFB700 100%)",
                  }}
                />
              </div>
              <div className="mt-1.5 text-[12px] text-[#7A7A82]">
                Осталось: 558 ккал
              </div>
            </div>

            {/* 3 макроса */}
            <div className="mt-5 grid grid-cols-3 gap-3">
              {MACROS.slice(1).map((m) => (
                <div key={m.key} className="flex flex-col">
                  <div className="text-[12px] text-[#B8B8BE] font-medium">
                    {m.label}
                  </div>
                  <div className="mt-0.5 text-[22px] font-bold tabular-nums leading-tight">
                    {m.eaten}
                    <span className="text-[13px] text-[#7A7A82] font-medium">
                      /{m.goal}
                    </span>
                  </div>
                  <div className="mt-2 h-1.5 rounded-full bg-[#242428] overflow-hidden">
                    <div
                      className="h-full rounded-full transition-[width] duration-500 ease-out"
                      style={{
                        width: `${pct(m.eaten, m.goal)}%`,
                        backgroundColor: m.color,
                      }}
                    />
                  </div>
                  <div className="mt-1 text-[11px] text-[#7A7A82]">
                    {pct(m.eaten, m.goal)}%
                  </div>
                </div>
              ))}
            </div>
          </Card>
        </section>

        {/* Переключатель Тренировка / Отдых */}
        <section aria-label="Режим дня">
          <div
            role="tablist"
            aria-label="Режим"
            className="relative flex items-center rounded-xl bg-[#1A1A1C] p-1 border border-white/[0.06]"
          >
            <button
              role="tab"
              aria-selected={mode === "training"}
              onClick={() => setMode("training")}
              className={`flex-1 h-10 rounded-lg text-[14px] font-semibold transition-colors flex items-center justify-center gap-2 ${
                mode === "training"
                  ? "bg-[#2A2A2E] text-white shadow-[0_2px_6px_rgba(0,0,0,0.35)]"
                  : "text-[#B8B8BE] hover:text-white"
              }`}
            >
              <Dumbbell className="h-4 w-4" strokeWidth={1.75} />
              Тренировка
            </button>
            <button
              role="tab"
              aria-selected={mode === "rest"}
              onClick={() => setMode("rest")}
              className={`flex-1 h-10 rounded-lg text-[14px] font-semibold transition-colors flex items-center justify-center gap-2 ${
                mode === "rest"
                  ? "bg-[#2A2A2E] text-white shadow-[0_2px_6px_rgba(0,0,0,0.35)]"
                  : "text-[#B8B8BE] hover:text-white"
              }`}
            >
              <Clock className="h-4 w-4" strokeWidth={1.75} />
              Отдых
            </button>
          </div>

          <div className="mt-3 flex items-center gap-2 text-[13px] text-[#B8B8BE]">
            <Flame className="h-4 w-4 text-[#FF6B00]" strokeWidth={1.75} />
            {mode === "training"
              ? "Тренировка сегодня в 19:00"
              : "День отдыха — белок норма, углеводы −20%"}
          </div>
        </section>

        {/* Приёмы пищи */}
        <section aria-label="Приёмы пищи">
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-[17px] font-semibold">Приёмы пищи</h2>
            <button className="text-[13px] text-[#FF6B00] font-semibold flex items-center gap-0.5 hover:text-[#FF8530]">
              Весь дневник
              <ChevronRight className="h-4 w-4" strokeWidth={1.75} />
            </button>
          </div>

          <ul className="space-y-3">
            {MEALS.map((meal) => (
              <li key={meal.id}>
                <Card className="bg-[#1A1A1C] border border-white/[0.06] rounded-2xl p-4 hover:bg-[#1E1E20] transition-colors cursor-pointer">
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 text-[#B8B8BE] text-[12px] font-medium">
                        <Clock className="h-3.5 w-3.5" strokeWidth={1.75} />
                        {meal.time}
                        <span className="text-white font-semibold text-[15px] ml-1">
                          {meal.title}
                        </span>
                      </div>
                      <div className="mt-1.5 text-[13px] text-[#B8B8BE] truncate">
                        {meal.items.join(" · ")}
                      </div>
                    </div>
                    <div className="text-right shrink-0">
                      <div className="text-[20px] font-bold tabular-nums leading-tight">
                        {meal.kcal}
                      </div>
                      <div className="text-[11px] text-[#7A7A82]">ккал</div>
                    </div>
                  </div>

                  <div className="mt-3 flex items-center gap-3 text-[12px] text-[#B8B8BE] font-medium tabular-nums">
                    <span>
                      Б <span className="text-white font-semibold">{meal.p}</span>
                    </span>
                    <span>
                      У <span className="text-white font-semibold">{meal.c}</span>
                    </span>
                    <span>
                      Ж <span className="text-white font-semibold">{meal.f}</span>
                    </span>
                  </div>
                </Card>
              </li>
            ))}
          </ul>
        </section>
      </main>

      {/* Floating Action Button */}
      <button
        aria-label="Записать приём пищи"
        className="fixed right-5 bottom-24 h-14 w-14 rounded-full bg-[#FF6B00] hover:bg-[#FF8530] active:bg-[#E55E00] active:scale-[0.98] text-[#0F0F10] shadow-[0_16px_40px_rgba(0,0,0,0.55),0_1px_0_0_rgba(255,255,255,0.08)_inset] flex items-center justify-center transition-all z-40"
      >
        <Plus className="h-6 w-6" strokeWidth={2.5} />
      </button>

      {/* Bottom Navigation */}
      <nav
        role="tablist"
        aria-label="Главная навигация"
        className="fixed bottom-0 inset-x-0 z-30 bg-[#0F0F10]/92 backdrop-blur border-t border-white/[0.06]"
      >
        <div className="mx-auto max-w-md px-2 h-[72px] grid grid-cols-5">
          <NavTab icon={<Home className="h-6 w-6" strokeWidth={1.75} />} label="Дом" active />
          <NavTab icon={<BookOpen className="h-6 w-6" strokeWidth={1.75} />} label="Дневник" />
          <NavTab
            icon={<Camera className="h-6 w-6" strokeWidth={2} />}
            label="Фото"
            center
          />
          <NavTab icon={<Zap className="h-6 w-6" strokeWidth={1.75} />} label="Спортпит" />
          <NavTab icon={<User className="h-6 w-6" strokeWidth={1.75} />} label="Я" />
        </div>
      </nav>
    </div>
  );
}

function NavTab({
  icon,
  label,
  active = false,
  center = false,
}: {
  icon: React.ReactNode;
  label: string;
  active?: boolean;
  center?: boolean;
}) {
  return (
    <button
      role="tab"
      aria-selected={active}
      aria-current={active ? "page" : undefined}
      className="flex flex-col items-center justify-center gap-1 h-full min-h-[52px] group"
    >
      {center ? (
        <span className="h-11 w-11 rounded-full bg-[#FF6B00] text-[#0F0F10] flex items-center justify-center shadow-[0_8px_24px_rgba(255,107,0,0.35)] group-active:scale-95 transition">
          {icon}
        </span>
      ) : (
        <span
          className={
            active ? "text-[#FF6B00]" : "text-[#7A7A82] group-hover:text-white"
          }
        >
          {icon}
        </span>
      )}
      <span
        className={`text-[11px] font-semibold tracking-[0.02em] ${
          active ? "text-[#FF6B00]" : "text-[#7A7A82]"
        }`}
      >
        {label}
      </span>
    </button>
  );
}
