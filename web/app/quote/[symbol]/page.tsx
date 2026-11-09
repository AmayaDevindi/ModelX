"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import Shell from "@/components/Shell";
import PriceChart from "@/components/PriceChart";
import TradingViewWidget from "@/components/TradingViewWidget";

interface Company {
  symbol: string;
  name: string;
  sector: string;
  last_price: number;
  change: number;
  change_pct: number;
}

interface ClusterInfo {
  symbol: string;
  tier: string;
  why: string;
}

export default function QuoteDetailPage() {
  const params = useParams<{ symbol: string }>();
  const symbol = decodeURIComponent(params.symbol);

  const [company, setCompany] = useState<Company | null>(null);
  const [history, setHistory] = useState<{ date: string; price: number }[] | null>(null);
  const [cluster, setCluster] = useState<ClusterInfo | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([
      fetch("/data/companies.json").then((r) => r.json()),
      fetch("/data/price_history.json").then((r) => r.json()),
      fetch("/data/company_clusters.json").then((r) => (r.ok ? r.json() : { companies: [] })),
    ])
      .then(([companiesData, historyData, clusterData]) => {
        const c = companiesData.companies.find((x: Company) => x.symbol === symbol);
        setCompany(c ?? null);
        setHistory(historyData.history[symbol] ?? []);
        const cl = (clusterData.companies ?? []).find((x: ClusterInfo) => x.symbol === symbol);
        setCluster(cl ?? null);
      })
      .catch((e: Error) => setError(e.message));
  }, [symbol]);

  return (
    <Shell>
      <div className="w-full max-w-2xl flex flex-col gap-5">
        <Link href="/quote" className="text-xs text-muted hover:text-accent">
          &larr; all companies
        </Link>

        {error && <p className="text-xs text-red-400">Could not load data: {error}</p>}
        {!company && !error && <p className="text-xs text-muted">Loading...</p>}

        {company && (
          <>
            <div>
              <div className="flex items-baseline gap-3">
                <h1 className="text-lg font-medium">{company.symbol}</h1>
                <span className="text-muted text-sm">{company.name}</span>
              </div>
              <p className="text-muted text-xs mt-0.5">{company.sector}</p>
              <div className="flex items-baseline gap-3 mt-2">
                <span className="text-2xl tabular-nums">Rs {company.last_price?.toFixed(2)}</span>
                <span
                  className={`text-sm tabular-nums ${
                    (company.change ?? 0) >= 0 ? "text-accent" : "text-red-400"
                  }`}
                >
                  {(company.change ?? 0) >= 0 ? "+" : ""}
                  {company.change} ({company.change_pct?.toFixed(2)}%)
                </span>
              </div>
            </div>

            <div>
              <TradingViewWidget symbol={company.symbol} />
              <p className="text-[10px] text-muted mt-1">Live chart powered by TradingView</p>
            </div>

            {history && history.length > 0 ? (
              <details className="text-xs">
                <summary className="text-muted cursor-pointer hover:text-accent">
                  Our own pulled price history (used for Model 1 &amp; 2 calculations)
                </summary>
                <div className="mt-2">
                  <PriceChart data={history} />
                </div>
              </details>
            ) : (
              <p className="text-xs text-muted">No price history available.</p>
            )}

            {cluster && (
              <div className="border border-border rounded px-4 py-3">
                <p className="text-xs text-accent mb-1">
                  Health group (Model 2): {cluster.tier}
                </p>
                <p className="text-xs text-muted leading-relaxed">{cluster.why}</p>
              </div>
            )}
          </>
        )}
      </div>
    </Shell>
  );
}
