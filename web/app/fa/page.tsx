"use client";

// Model 2 (reduced scope): k-means clusters S&P SL20 companies by real
// features (volatility, beta, board independence, auditor, 12-month price
// range), not the full profitability/earnings scoring - see README and
// docs/decisions.md (D50) for why.
import { useEffect, useState } from "react";
import Shell from "@/components/Shell";

interface Company {
  symbol: string;
  sector: string;
  tier: string;
  why: string;
  volatility: number;
  beta: number;
  independent_ratio: number;
  is_big4_auditor: number;
  position_in_52wk_range: number;
}

interface Payload {
  generated_at: string;
  companies: Company[];
}

const TIER_ORDER = ["Lower price volatility", "Medium price volatility", "Higher price volatility"];

export default function FAPage() {
  const [data, setData] = useState<Payload | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch("/data/company_clusters.json")
      .then((r) => {
        if (!r.ok) throw new Error(`status ${r.status}`);
        return r.json();
      })
      .then(setData)
      .catch((e: Error) => setError(e.message));
  }, []);

  return (
    <Shell>
      <div className="w-full max-w-3xl flex flex-col gap-6">
        <div>
          <h1 className="text-accent text-sm font-medium mb-1">Company health groups (Model 2)</h1>
          <p className="text-muted text-xs leading-relaxed">
            Grouped by k-means clustering (an unsupervised machine-learning method, written by
            hand) on 5 real features per company: price volatility, beta vs. the market, board
            independence, whether the auditor is a Big 4 firm, and where today&apos;s price sits
            in its 12-month range. This is a reduced version of fundamental analysis - full
            profitability and earnings scoring needs the annual-report PDFs, which needed more
            time than this submission had. Groups are labelled only by volatility; governance
            stats are shown separately, not folded into one verdict.
          </p>
        </div>

        {error && <p className="text-xs text-red-400">Could not load company data: {error}</p>}
        {!data && !error && <p className="text-xs text-muted">Loading...</p>}

        {data &&
          TIER_ORDER.map((tier) => {
            const group = data.companies.filter((c) => c.tier === tier);
            if (!group.length) return null;
            const avgVol = group.reduce((s, c) => s + c.volatility, 0) / group.length;
            const avgInd = group.reduce((s, c) => s + c.independent_ratio, 0) / group.length;
            const big4Pct = group.reduce((s, c) => s + c.is_big4_auditor, 0) / group.length;
            return (
              <div key={tier} className="border border-border rounded">
                <div className="px-4 py-2.5 border-b border-border bg-white/[0.02]">
                  <span className="text-accent text-sm">{tier}</span>
                  <span className="text-muted text-xs ml-3">
                    {group.length} companies &middot; avg volatility {avgVol.toFixed(1)}% &middot; avg
                    board independence {(avgInd * 100).toFixed(0)}% &middot; Big 4 auditor{" "}
                    {(big4Pct * 100).toFixed(0)}% of the time
                  </span>
                </div>
                <div className="divide-y divide-border">
                  {group.map((c) => (
                    <div key={c.symbol} className="px-4 py-2 flex flex-col sm:flex-row sm:items-baseline gap-x-3 text-sm">
                      <span className="font-medium w-28 shrink-0">{c.symbol}</span>
                      <span className="text-muted text-xs w-40 shrink-0">{c.sector}</span>
                      <span className="text-muted text-xs">{c.why}</span>
                    </div>
                  ))}
                </div>
              </div>
            );
          })}
      </div>
    </Shell>
  );
}
