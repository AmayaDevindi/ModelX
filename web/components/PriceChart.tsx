"use client";

// A plain hand-drawn SVG line chart - no charting library, so there's
// nothing new to install (today already hit one blocked-dependency issue,
// so keeping this dependency-free on purpose).
import { useMemo, useState } from "react";

interface Point {
  date: string;
  price: number;
}

const RANGES: { label: string; days: number | null }[] = [
  { label: "1M", days: 30 },
  { label: "3M", days: 90 },
  { label: "6M", days: 180 },
  { label: "1Y", days: null },
];

export default function PriceChart({ data }: { data: Point[] }) {
  const [range, setRange] = useState("1Y");

  const filtered = useMemo(() => {
    const r = RANGES.find((r) => r.label === range)!;
    if (r.days == null) return data;
    return data.slice(-r.days);
  }, [data, range]);

  const width = 600;
  const height = 200;
  const padding = 8;

  const { path, min, max } = useMemo(() => {
    if (filtered.length < 2) return { path: "", min: 0, max: 0 };
    const prices = filtered.map((d) => d.price);
    const lo = Math.min(...prices);
    const hi = Math.max(...prices);
    const span = hi - lo || 1;
    const stepX = (width - padding * 2) / (filtered.length - 1);
    const points = filtered.map((d, i) => {
      const x = padding + i * stepX;
      const y = padding + (1 - (d.price - lo) / span) * (height - padding * 2);
      return `${x.toFixed(1)},${y.toFixed(1)}`;
    });
    return { path: "M" + points.join(" L"), min: lo, max: hi };
  }, [filtered]);

  if (filtered.length < 2) {
    return <p className="text-xs text-muted">Not enough price history to chart.</p>;
  }

  const first = filtered[0];
  const last = filtered[filtered.length - 1];
  const changePct = ((last.price - first.price) / first.price) * 100;
  const positive = changePct >= 0;

  return (
    <div className="w-full">
      <div className="flex items-center justify-between mb-2">
        <div className="flex gap-1">
          {RANGES.map((r) => (
            <button
              key={r.label}
              onClick={() => setRange(r.label)}
              className={`text-xs px-2 py-1 rounded border ${
                range === r.label
                  ? "border-accent text-accent"
                  : "border-border text-muted hover:text-foreground"
              }`}
            >
              {r.label}
            </button>
          ))}
        </div>
        <span className={`text-sm tabular-nums ${positive ? "text-accent" : "text-red-400"}`}>
          {positive ? "+" : ""}
          {changePct.toFixed(1)}% over this range
        </span>
      </div>
      <svg viewBox={`0 0 ${width} ${height}`} className="w-full h-48" preserveAspectRatio="none">
        <path d={path} fill="none" stroke={positive ? "#4ade80" : "#f87171"} strokeWidth={1.5} />
      </svg>
      <div className="flex justify-between text-[11px] text-muted mt-1">
        <span>Rs {min.toFixed(2)}</span>
        <span>{first.date}</span>
        <span>{last.date}</span>
        <span>Rs {max.toFixed(2)}</span>
      </div>
    </div>
  );
}
