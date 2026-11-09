// A plain, readable view of a portfolio split - a bar and a percentage per
// asset, nothing technical-looking. Used both in the quiz result and on the
// main PLAN screen so the two always look the same.
import { ASSETS, type Split } from "@/lib/profile";

export default function SplitView({ split }: { split: Split }) {
  return (
    <div className="w-full flex flex-col gap-2.5">
      {ASSETS.map((asset) => {
        const pct = split[asset];
        return (
          <div key={asset} className="flex items-center gap-3 text-sm">
            <span className="w-36 shrink-0 text-muted">{asset}</span>
            <div className="flex-1 h-2 bg-border rounded overflow-hidden">
              <div className="h-full bg-accent rounded" style={{ width: `${pct}%` }} />
            </div>
            <span className="w-10 text-right tabular-nums">{pct}%</span>
          </div>
        );
      })}
    </div>
  );
}
