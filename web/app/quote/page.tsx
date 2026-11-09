"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import Shell from "@/components/Shell";

interface Company {
  symbol: string;
  name: string;
  sector: string;
  last_price: number;
  change: number;
  change_pct: number;
}

export default function QuoteListPage() {
  const [companies, setCompanies] = useState<Company[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch("/data/companies.json")
      .then((r) => {
        if (!r.ok) throw new Error(`status ${r.status}`);
        return r.json();
      })
      .then((d) => setCompanies(d.companies))
      .catch((e: Error) => setError(e.message));
  }, []);

  return (
    <Shell>
      <div className="w-full max-w-2xl flex flex-col gap-4">
        <h1 className="text-accent text-sm font-medium">S&amp;P SL20 companies</h1>
        {error && <p className="text-xs text-red-400">Could not load company data: {error}</p>}
        {!companies && !error && <p className="text-xs text-muted">Loading...</p>}

        {companies && (
          <div className="border border-border rounded divide-y divide-border">
            {companies.map((c) => {
              const positive = (c.change ?? 0) >= 0;
              return (
                <Link
                  key={c.symbol}
                  href={`/quote/${c.symbol}`}
                  className="flex items-center justify-between px-4 py-2.5 text-sm hover:bg-white/[0.03] transition-colors"
                >
                  <div className="flex flex-col">
                    <span className="font-medium">{c.symbol}</span>
                    <span className="text-muted text-xs">{c.name}</span>
                  </div>
                  <span className="text-muted text-xs hidden sm:block">{c.sector}</span>
                  <div className="flex flex-col items-end">
                    <span className="tabular-nums">Rs {c.last_price?.toFixed(2)}</span>
                    <span className={`text-xs tabular-nums ${positive ? "text-accent" : "text-red-400"}`}>
                      {positive ? "+" : ""}
                      {c.change_pct?.toFixed(2)}%
                    </span>
                  </div>
                </Link>
              );
            })}
          </div>
        )}
      </div>
    </Shell>
  );
}
