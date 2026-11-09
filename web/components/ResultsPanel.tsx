"use client";

// Takes the split from the quiz and shows: the split itself, an amount/years
// input, and what the Monte Carlo simulation says could happen - plus a
// plain comparison against "what if I just put it all in a fixed deposit".
import { useEffect, useMemo, useState } from "react";
import type { Split } from "@/lib/profile";
import { simulate } from "@/lib/simulate";
import { loadAssumptions, type AssumptionsData } from "@/lib/loadAssumptions";
import SplitView from "@/components/SplitView";
import { ASSETS } from "@/lib/profile";

const ALL_FD_SPLIT: Split = {
  Savings: 0,
  "Fixed deposits": 100,
  "T-bills & bonds": 0,
  "Unit trusts": 0,
  "Shares (S&P SL20)": 0,
};

function formatRs(n: number) {
  return "Rs " + Math.round(n).toLocaleString("en-LK");
}

export default function ResultsPanel({ split }: { split: Split }) {
  const [amount, setAmount] = useState(500_000);
  const [years, setYears] = useState(5);
  const [data, setData] = useState<AssumptionsData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [showWhy, setShowWhy] = useState(false);

  useEffect(() => {
    loadAssumptions()
      .then(setData)
      .catch((e: Error) => setError(e.message));
  }, []);

  const result = useMemo(() => {
    if (!data || amount <= 0 || years <= 0) return null;
    return simulate(split, amount, years, data.inflation, data.assumptions);
  }, [data, split, amount, years]);

  const fdOnly = useMemo(() => {
    if (!data || amount <= 0 || years <= 0) return null;
    return simulate(ALL_FD_SPLIT, amount, years, data.inflation, data.assumptions);
  }, [data, amount, years]);

  if (error) {
    return <p className="text-xs text-red-400 text-center">Could not load the model&apos;s numbers: {error}</p>;
  }
  if (!data) {
    return <p className="text-xs text-muted">Loading the latest numbers...</p>;
  }

  return (
    <div className="w-full flex flex-col gap-5">
      <SplitView split={split} />

      <div className="flex gap-3 text-sm">
        <label className="flex-1 flex flex-col gap-1">
          <span className="text-muted text-xs">Amount (Rs)</span>
          <input
            type="number"
            min={1000}
            step={1000}
            value={amount}
            onChange={(e) => setAmount(Number(e.target.value))}
            className="bg-transparent border border-border rounded px-2 py-1.5 outline-none focus:border-accent tabular-nums"
          />
        </label>
        <label className="flex-1 flex flex-col gap-1">
          <span className="text-muted text-xs">Years</span>
          <input
            type="number"
            min={1}
            max={30}
            step={1}
            value={years}
            onChange={(e) => setYears(Number(e.target.value))}
            className="bg-transparent border border-border rounded px-2 py-1.5 outline-none focus:border-accent tabular-nums"
          />
        </label>
      </div>

      {result && (
        <div className="flex flex-col gap-2 text-sm border-t border-border pt-4">
          <Row label="Bad case (unlucky)" value={formatRs(result.badCase)} />
          <Row label="Likely case" value={formatRs(result.middleCase)} />
          <Row label="Good case (lucky)" value={formatRs(result.goodCase)} />
          <Row
            label="Chance of ending with less than you put in"
            value={`${(result.chanceOfLoss * 100).toFixed(0)}%`}
          />
          <Row
            label="Chance of beating inflation"
            value={`${(result.chanceBeatsInflation * 100).toFixed(0)}%`}
          />
        </div>
      )}

      {fdOnly && result && (
        <p className="text-xs text-muted leading-relaxed border-t border-border pt-4">
          For comparison, putting all of it in a fixed deposit instead would likely give you about{" "}
          {formatRs(fdOnly.middleCase)}, beating inflation {Math.round(fdOnly.chanceBeatsInflation * 100)}% of
          the time &mdash; versus {Math.round(result.chanceBeatsInflation * 100)}% with the split above.
        </p>
      )}

      <div className="border-t border-border pt-4">
        <button
          onClick={() => setShowWhy((v) => !v)}
          className="text-xs text-muted hover:text-accent underline"
        >
          {showWhy ? "hide" : "why these numbers?"}
        </button>
        {showWhy && (
          <ul className="mt-3 flex flex-col gap-2 text-[11px] text-muted leading-relaxed">
            {ASSETS.filter((asset) => split[asset] > 0).map((asset) => (
              <li key={asset}>
                <span className="text-foreground">{asset}:</span> {data.notes[asset]}
              </li>
            ))}
          </ul>
        )}
      </div>

      <p className="text-[11px] text-muted/70 leading-relaxed">
        Inflation assumed at {data.inflation.toFixed(1)}% ({data.inflationMonth}). This is a model for
        learning, not financial advice &mdash; real returns will differ.
      </p>
    </div>
  );
}

function Row({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex justify-between gap-3">
      <span className="text-muted">{label}</span>
      <span className="tabular-nums">{value}</span>
    </div>
  );
}
