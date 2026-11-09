"use client";

// Model 4 (added late, 9 Nov): shows the AR forecast + its honest backtest
// result for the one or two stocks it covers (see src/model/price_forecast.py
// and docs/decisions.md D53 for exactly what this is and isn't).
interface ForecastPoint {
  date: string;
  price: number;
  low: number;
  high: number;
}

interface ForecastCompany {
  symbol: string;
  ar_order: number;
  backtest: { holdout_days: number; ar_rmse: number; naive_rmse: number; winner: string };
  last_price: number;
  last_date: string;
  forecast: ForecastPoint[];
}

export default function ForecastPanel({ data }: { data: ForecastCompany }) {
  const width = 600;
  const height = 180;
  const padding = 8;

  const allValues = data.forecast.flatMap((f) => [f.low, f.high]);
  allValues.push(data.last_price);
  const lo = Math.min(...allValues);
  const hi = Math.max(...allValues);
  const span = hi - lo || 1;
  const n = data.forecast.length;
  const stepX = (width - padding * 2) / n;

  const toXY = (i: number, value: number): [number, number] => {
    const x = padding + (i + 1) * stepX;
    const y = padding + (1 - (value - lo) / span) * (height - padding * 2);
    return [x, y];
  };

  const startX = padding;
  const startY = padding + (1 - (data.last_price - lo) / span) * (height - padding * 2);
  const start: [number, number] = [startX, startY];

  const centerPoints: [number, number][] = [
    start,
    ...data.forecast.map((f, i) => toXY(i, f.price)),
  ];
  const centerPath = "M" + centerPoints.map(([x, y]) => `${x.toFixed(1)},${y.toFixed(1)}`).join(" L");

  const highPoints: [number, number][] = [start, ...data.forecast.map((f, i) => toXY(i, f.high))];
  const lowPoints: [number, number][] = [start, ...data.forecast.map((f, i) => toXY(i, f.low))].reverse();
  const bandPath =
    "M" + [...highPoints, ...lowPoints].map(([x, y]) => `${x.toFixed(1)},${y.toFixed(1)}`).join(" L") + " Z";

  const last = data.forecast[data.forecast.length - 1];
  const arBetter = data.backtest.winner === "AR";

  return (
    <div className="border border-border rounded px-4 py-3">
      <p className="text-xs text-accent mb-1">
        {data.forecast.length}-day price projection (Model 4, exploratory)
      </p>
      <svg viewBox={`0 0 ${width} ${height}`} className="w-full h-40" preserveAspectRatio="none">
        <path d={bandPath} fill="#4ade80" opacity={0.12} stroke="none" />
        <path d={centerPath} fill="none" stroke="#4ade80" strokeWidth={1.5} />
      </svg>
      <div className="flex justify-between text-[11px] text-muted mt-1">
        <span>Rs {data.last_price.toFixed(2)} ({data.last_date})</span>
        <span>Rs {last.price.toFixed(2)} ({last.date})</span>
      </div>
      <p className="text-[11px] text-muted mt-2 leading-relaxed">
        80% range on the last day: Rs {last.low.toFixed(2)} - Rs {last.high.toFixed(2)}.
        Backtest on the last {data.backtest.holdout_days} days: this model&apos;s average error was
        Rs {data.backtest.ar_rmse.toFixed(2)} vs. Rs {data.backtest.naive_rmse.toFixed(2)} for simply
        guessing &quot;no change&quot; - {arBetter ? "the model beat that simple guess" : "the simple guess actually did better here"}.
        A simplified AR({data.ar_order}) model (no moving-average term), hand-written and validated
        on roughly 240 days of price history - not a trading signal. See README.
      </p>
    </div>
  );
}
