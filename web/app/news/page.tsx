"use client";

// Model 3 (reduced scope): tags headlines with an economic factor and
// direction, then follows a fixed, hand-written factor-to-sector effect
// table - our own reasoning, not a licensed adviser's, and not yet
// backtested - see README and docs/decisions.md (D51).
import { useEffect, useState } from "react";
import Shell from "@/components/Shell";

interface Tag {
  published: string;
  title: string;
  link: string;
  factor: string;
  direction: string;
  effects: string;
  confidence: string;
}

interface Payload {
  generated_at: string;
  tags: Tag[];
}

export default function NewsPage() {
  const [data, setData] = useState<Payload | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch("/data/news_chain.json")
      .then((r) => {
        if (!r.ok) throw new Error(`status ${r.status}`);
        return r.json();
      })
      .then(setData)
      .catch((e: Error) => setError(e.message));
  }, []);

  return (
    <Shell>
      <div className="w-full max-w-2xl flex flex-col gap-6">
        <div>
          <h1 className="text-accent text-sm font-medium mb-1">News chain reaction (Model 3)</h1>
          <p className="text-muted text-xs leading-relaxed">
            Headlines tagged with an economic factor (oil, interest rates, the rupee, inflation,
            tourism, tax) and a direction read from the headline&apos;s own wording, then a fixed
            table of which sectors that typically helps or hurts and why. These are our own
            common-knowledge rules, not reviewed by a licensed adviser and not yet tested against
            how prices actually moved - treat them as a starting point for thinking, not a
            prediction.
          </p>
        </div>

        {error && <p className="text-xs text-red-400">Could not load news data: {error}</p>}
        {!data && !error && <p className="text-xs text-muted">Loading...</p>}
        {data && data.tags.length === 0 && (
          <p className="text-xs text-muted">No headlines currently match a tracked economic factor.</p>
        )}

        {data &&
          data.tags.map((t, i) => (
            <div key={i} className="border border-border rounded px-4 py-3">
              <div className="flex items-baseline justify-between gap-3 mb-1">
                <span className="text-xs text-muted">{t.published}</span>
                <span className="text-xs text-accent">
                  {t.factor} &middot; {t.direction}
                </span>
              </div>
              <a
                href={t.link}
                target="_blank"
                rel="noopener noreferrer"
                className="text-sm hover:underline"
              >
                {t.title}
              </a>
              {t.effects && <p className="text-xs text-muted mt-2 leading-relaxed">{t.effects}</p>}
              <p className="text-[11px] text-muted/60 mt-1">confidence: {t.confidence}</p>
            </div>
          ))}
      </div>
    </Shell>
  );
}
