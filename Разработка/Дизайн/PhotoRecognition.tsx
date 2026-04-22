"use client";

import * as React from "react";
// shadcn/ui stubs — в реальном проекте заменить на "@/components/ui/*"
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import {
  ArrowLeft,
  Camera,
  ImagePlus,
  Sparkles,
  Minus,
  Plus,
  Check,
  RotateCcw,
  AlertTriangle,
  Loader2,
} from "lucide-react";

/**
 * GymFuel AI — Photo Recognition
 * Три состояния в одном файле:
 *   A) empty  — пустой экран: камера / загрузить
 *   B) loading — распознавание (сканирующая линия)
 *   C) result — список распознанных продуктов с редактированием граммовки
 *
 * Состояние переключается верхним segmented control — для демо/превью.
 */

type State = "empty" | "loading" | "result";

type RecognizedItem = {
  id: string;
  name: string;
  grams: number;
  confidence: "high" | "low";
  kcalPer100: number;
  pPer100: number;
  cPer100: number;
  fPer100: number;
};

const INITIAL: RecognizedItem[] = [
  {
    id: "1",
    name: "Куриная грудка",
    grams: 200,
    confidence: "high",
    kcalPer100: 165,
    pPer100: 31,
    cPer100: 0,
    fPer100: 3.6,
  },
  {
    id: "2",
    name: "Рис басмати отварной",
    grams: 150,
    confidence: "high",
    kcalPer100: 120,
    pPer100: 2.7,
    cPer100: 26,
    fPer100: 0.3,
  },
  {
    id: "3",
    name: "Оливковое масло",
    grams: 10,
    confidence: "low",
    kcalPer100: 884,
    pPer100: 0,
    cPer100: 0,
    fPer100: 100,
  },
];

function calc(item: RecognizedItem) {
  const k = item.grams / 100;
  return {
    kcal: Math.round(item.kcalPer100 * k),
    p: Math.round(item.pPer100 * k * 10) / 10,
    c: Math.round(item.cPer100 * k * 10) / 10,
    f: Math.round(item.fPer100 * k * 10) / 10,
  };
}

export default function PhotoRecognition() {
  const [state, setState] = React.useState<State>("empty");
  const [items, setItems] = React.useState<RecognizedItem[]>(INITIAL);

  const totals = items.reduce(
    (acc, it) => {
      const c = calc(it);
      acc.kcal += c.kcal;
      acc.p += c.p;
      acc.c += c.c;
      acc.f += c.f;
      return acc;
    },
    { kcal: 0, p: 0, c: 0, f: 0 }
  );

  return (
    <div className="min-h-screen bg-[#0F0F10] text-white font-[Inter,system-ui,-apple-system,sans-serif] antialiased">
      {/* Header */}
      <header className="sticky top-0 z-30 bg-[#0F0F10]/92 backdrop-blur border-b border-white/[0.06]">
        <div className="mx-auto max-w-md px-4 h-14 flex items-center justify-between">
          <button
            aria-label="Назад"
            className="h-11 w-11 -ml-2 rounded-full flex items-center justify-center hover:bg-white/[0.04] transition"
          >
            <ArrowLeft className="h-6 w-6" strokeWidth={1.75} />
          </button>
          <h1 className="text-[15px] font-semibold">
            {state === "empty" && "Фото еды"}
            {state === "loading" && "Распознаю…"}
            {state === "result" && "Что в кадре"}
          </h1>
          <div className="w-11" />
        </div>
      </header>

      {/* Demo state switcher (служебный, для превью) */}
      <div className="mx-auto max-w-md px-4 pt-3">
        <div
          role="tablist"
          aria-label="Демо состояний"
          className="flex items-center rounded-xl bg-[#1A1A1C] p-1 border border-white/[0.06] text-[12px] font-semibold"
        >
          {(["empty", "loading", "result"] as const).map((s) => (
            <button
              key={s}
              role="tab"
              aria-selected={state === s}
              onClick={() => setState(s)}
              className={`flex-1 h-8 rounded-lg transition-colors ${
                state === s
                  ? "bg-[#2A2A2E] text-white"
                  : "text-[#7A7A82] hover:text-white"
              }`}
            >
              {s === "empty" ? "А) Пусто" : s === "loading" ? "Б) Распознаю" : "В) Результат"}
            </button>
          ))}
        </div>
      </div>

      <main className="mx-auto max-w-md px-4 pt-4 pb-10">
        {state === "empty" && <EmptyState />}
        {state === "loading" && <LoadingState />}
        {state === "result" && (
          <ResultState items={items} setItems={setItems} totals={totals} />
        )}
      </main>
    </div>
  );
}

/* ─────────── A) Empty ─────────── */
function EmptyState() {
  return (
    <section className="space-y-4">
      {/* Камера-рамка */}
      <div className="relative aspect-[4/3] w-full rounded-2xl overflow-hidden border border-white/[0.08] bg-[#1A1A1C] flex items-center justify-center">
        {/* Сетка-«видоискатель» */}
        <div
          className="absolute inset-0 opacity-[0.08]"
          style={{
            backgroundImage:
              "linear-gradient(#fff 1px, transparent 1px), linear-gradient(90deg, #fff 1px, transparent 1px)",
            backgroundSize: "32px 32px",
          }}
        />
        {/* Уголки рамки */}
        <Corner className="top-4 left-4" dir="tl" />
        <Corner className="top-4 right-4" dir="tr" />
        <Corner className="bottom-4 left-4" dir="bl" />
        <Corner className="bottom-4 right-4" dir="br" />

        <div className="relative z-10 flex flex-col items-center gap-2 text-center px-6">
          <div className="h-16 w-16 rounded-full bg-[#FF6B00]/15 flex items-center justify-center">
            <Camera className="h-7 w-7 text-[#FF6B00]" strokeWidth={1.75} />
          </div>
          <div className="text-[17px] font-semibold">Сними еду</div>
          <div className="text-[13px] text-[#B8B8BE] leading-snug">
            Держи тарелку в кадре целиком.
            <br />
            Свет сверху, без бликов.
          </div>
        </div>
      </div>

      {/* CTAs */}
      <div className="space-y-3">
        <button className="h-[52px] w-full rounded-xl bg-[#FF6B00] hover:bg-[#FF8530] active:bg-[#E55E00] active:scale-[0.98] text-[#0F0F10] font-bold text-[16px] flex items-center justify-center gap-2 transition">
          <Camera className="h-5 w-5" strokeWidth={2.25} />
          Снять сейчас
        </button>
        <button className="h-[52px] w-full rounded-xl bg-[#1A1A1C] border border-white/[0.08] hover:bg-[#242428] text-white font-semibold text-[16px] flex items-center justify-center gap-2 transition">
          <ImagePlus className="h-5 w-5" strokeWidth={1.75} />
          Загрузить из галереи
        </button>
      </div>

      <div className="pt-2 text-center text-[12px] text-[#7A7A82]">
        Распознаём блюдо и КБЖУ за 3–5 секунд
      </div>
    </section>
  );
}

function Corner({ className, dir }: { className?: string; dir: "tl" | "tr" | "bl" | "br" }) {
  const borders: Record<string, string> = {
    tl: "border-t-2 border-l-2 rounded-tl-xl",
    tr: "border-t-2 border-r-2 rounded-tr-xl",
    bl: "border-b-2 border-l-2 rounded-bl-xl",
    br: "border-b-2 border-r-2 rounded-br-xl",
  };
  return (
    <span
      aria-hidden="true"
      className={`absolute h-8 w-8 border-[#FF6B00] ${borders[dir]} ${className ?? ""}`}
    />
  );
}

/* ─────────── B) Loading ─────────── */
function LoadingState() {
  return (
    <section className="space-y-4">
      <div className="relative aspect-[4/3] w-full rounded-2xl overflow-hidden border border-white/[0.08] bg-gradient-to-br from-[#1A1A1C] to-[#242428]">
        {/* Имитация фото */}
        <div
          className="absolute inset-0 opacity-60"
          style={{
            background:
              "radial-gradient(circle at 30% 40%, #3a2a1a 0%, transparent 40%), radial-gradient(circle at 70% 60%, #2a1f12 0%, transparent 50%)",
          }}
        />
        {/* Сканирующая линия */}
        <div className="absolute inset-x-0 top-0 h-[2px] bg-gradient-to-b from-[#FF6B00] to-transparent animate-scan" />
        {/* Overlay blur */}
        <div className="absolute inset-0 bg-[#0F0F10]/50 backdrop-blur-[2px]" />

        <div className="relative z-10 h-full w-full flex flex-col items-center justify-center gap-3">
          <Loader2 className="h-8 w-8 text-[#FF6B00] animate-spin" strokeWidth={2} />
          <div className="text-[20px] font-bold">Распознаю…</div>
          <div className="text-[13px] text-[#B8B8BE]">Обычно 3–5 секунд</div>
        </div>
      </div>

      {/* Skeleton-список */}
      <div className="space-y-2">
        {[1, 2, 3].map((i) => (
          <div
            key={i}
            className="h-16 rounded-xl bg-gradient-to-r from-[#1A1A1C] via-[#242428] to-[#1A1A1C] bg-[length:200%_100%] animate-shimmer"
          />
        ))}
      </div>

      {/* Inline styles для анимаций (в реальном проекте — в globals.css / tailwind.config) */}
      <style>{`
        @keyframes scan {
          0% { transform: translateY(0); }
          50% { transform: translateY(calc(var(--h, 300px) - 2px)); }
          100% { transform: translateY(0); }
        }
        .animate-scan { animation: scan 2.5s ease-in-out infinite; height: 2px; box-shadow: 0 0 24px 4px #FF6B00; }

        @keyframes shimmer {
          0% { background-position: 200% 0; }
          100% { background-position: -200% 0; }
        }
        .animate-shimmer { animation: shimmer 1.5s linear infinite; }
      `}</style>
    </section>
  );
}

/* ─────────── C) Result ─────────── */
function ResultState({
  items,
  setItems,
  totals,
}: {
  items: RecognizedItem[];
  setItems: React.Dispatch<React.SetStateAction<RecognizedItem[]>>;
  totals: { kcal: number; p: number; c: number; f: number };
}) {
  const updateGrams = (id: string, delta: number) => {
    setItems((prev) =>
      prev.map((it) =>
        it.id === id ? { ...it, grams: Math.max(0, it.grams + delta) } : it
      )
    );
  };

  const setGrams = (id: string, val: number) => {
    setItems((prev) =>
      prev.map((it) => (it.id === id ? { ...it, grams: Math.max(0, val) } : it))
    );
  };

  return (
    <section className="space-y-4 pb-28">
      {/* Thumbnail + название */}
      <div className="flex items-center gap-3 rounded-xl bg-[#1A1A1C] border border-white/[0.06] p-3">
        <div
          className="h-12 w-12 rounded-lg shrink-0 bg-gradient-to-br from-[#3a2a1a] to-[#2a1f12] border border-white/[0.08]"
          aria-hidden
        />
        <div className="min-w-0">
          <div className="text-[15px] font-semibold truncate">Обед</div>
          <div className="text-[12px] text-[#B8B8BE] truncate">
            3 продукта распознано
          </div>
        </div>
        <button className="ml-auto h-9 px-3 rounded-lg bg-[#242428] hover:bg-[#2A2A2E] text-[12px] font-semibold transition">
          Переснять
        </button>
      </div>

      {/* Итоги */}
      <div className="rounded-2xl bg-[#1A1A1C] border border-white/[0.06] p-4">
        <div className="text-[12px] text-[#B8B8BE] uppercase tracking-wider font-medium">
          Итого
        </div>
        <div className="mt-1 flex items-baseline gap-2">
          <span className="text-[40px] leading-none font-extrabold tabular-nums">
            {totals.kcal}
          </span>
          <span className="text-[15px] text-[#B8B8BE]">ккал</span>
        </div>
        <div className="mt-3 grid grid-cols-3 gap-3 text-[13px]">
          <MacroPill label="Б" val={totals.p} color="#3B9EFF" />
          <MacroPill label="У" val={totals.c} color="#F5C842" />
          <MacroPill label="Ж" val={totals.f} color="#A371F7" />
        </div>
      </div>

      {/* Список распознанных */}
      <ul className="space-y-3">
        {items.map((it) => {
          const c = calc(it);
          return (
            <li key={it.id}>
              <Card className="bg-[#1A1A1C] border border-white/[0.06] rounded-2xl p-4">
                <div className="flex items-start justify-between gap-2">
                  <div className="min-w-0 flex-1">
                    <div className="text-[15px] font-semibold truncate">
                      {it.name}
                    </div>
                    <div className="mt-1 flex items-center gap-3 text-[12px] text-[#B8B8BE] tabular-nums">
                      <span>
                        <span className="text-white font-semibold">{c.kcal}</span> ккал
                      </span>
                      <span>Б {c.p}</span>
                      <span>У {c.c}</span>
                      <span>Ж {c.f}</span>
                    </div>
                  </div>
                </div>

                {it.confidence === "low" && (
                  <div className="mt-2 flex items-center gap-2 rounded-lg bg-[rgba(255,183,0,0.14)] border border-[rgba(255,183,0,0.3)] px-2.5 py-1.5">
                    <AlertTriangle
                      className="h-4 w-4 text-[#FFB700] shrink-0"
                      strokeWidth={2}
                    />
                    <span className="text-[12px] text-[#FFB700]">
                      Не уверен. Проверь название и граммовку.
                    </span>
                  </div>
                )}

                {/* Stepper граммовки */}
                <div className="mt-3 flex items-center gap-2">
                  <button
                    aria-label="Уменьшить граммовку"
                    onClick={() => updateGrams(it.id, -10)}
                    className="h-11 w-11 rounded-xl bg-[#242428] hover:bg-[#2A2A2E] active:scale-95 flex items-center justify-center transition"
                  >
                    <Minus className="h-4 w-4" strokeWidth={2.5} />
                  </button>

                  <div className="flex-1 flex items-center justify-center rounded-xl bg-[#242428] h-11 px-3">
                    <input
                      type="number"
                      inputMode="numeric"
                      value={it.grams}
                      onChange={(e) => setGrams(it.id, Number(e.target.value))}
                      className="w-full bg-transparent text-center text-[16px] font-bold tabular-nums text-white outline-none"
                      aria-label={`Граммовка ${it.name}`}
                    />
                    <span className="text-[13px] text-[#7A7A82] ml-1">г</span>
                  </div>

                  <button
                    aria-label="Увеличить граммовку"
                    onClick={() => updateGrams(it.id, 10)}
                    className="h-11 w-11 rounded-xl bg-[#242428] hover:bg-[#2A2A2E] active:scale-95 flex items-center justify-center transition"
                  >
                    <Plus className="h-4 w-4" strokeWidth={2.5} />
                  </button>
                </div>
              </Card>
            </li>
          );
        })}

        {/* Добавить вручную */}
        <li>
          <button className="w-full h-[52px] rounded-xl border border-dashed border-white/[0.15] text-[#B8B8BE] hover:text-white hover:border-white/[0.3] text-[14px] font-semibold flex items-center justify-center gap-2 transition">
            <Plus className="h-4 w-4" strokeWidth={2} />
            Добавить продукт вручную
          </button>
        </li>
      </ul>

      {/* Sticky Save */}
      <div className="fixed inset-x-0 bottom-0 z-30 bg-gradient-to-t from-[#0F0F10] via-[#0F0F10] to-transparent pt-6 pb-5">
        <div className="mx-auto max-w-md px-4">
          <button className="h-[52px] w-full rounded-xl bg-[#FF6B00] hover:bg-[#FF8530] active:bg-[#E55E00] active:scale-[0.98] text-[#0F0F10] font-bold text-[16px] flex items-center justify-center gap-2 transition shadow-[0_16px_40px_rgba(255,107,0,0.25)]">
            <Check className="h-5 w-5" strokeWidth={2.5} />
            Записать в дневник
          </button>
        </div>
      </div>
    </section>
  );
}

function MacroPill({
  label,
  val,
  color,
}: {
  label: string;
  val: number;
  color: string;
}) {
  return (
    <div className="rounded-lg bg-[#242428] px-2.5 py-2 flex items-center gap-2">
      <span
        className="h-2 w-2 rounded-full shrink-0"
        style={{ backgroundColor: color }}
      />
      <span className="text-[12px] text-[#B8B8BE] font-medium">{label}</span>
      <span className="ml-auto text-[14px] font-bold tabular-nums">
        {val}
        <span className="text-[11px] text-[#7A7A82] font-medium ml-0.5">г</span>
      </span>
    </div>
  );
}
