// Reads web/public/data/assumptions.json - the file the data pipeline writes
// every time it runs (src/data/export_model_json.py). This is what makes the
// site's numbers update automatically: whoever runs the pipeline next writes
// a new copy of this file, and the website picks it up next time someone
// loads the page - no code change needed.
import { ASSETS, type Asset } from "./profile";
import type { Assumptions } from "./simulate";

export interface AssumptionsData {
  assumptions: Assumptions;
  notes: Record<Asset, string>;
  inflation: number;
  inflationMonth: string;
  generatedAt: string;
}

interface RawAssetEntry {
  name: string;
  mean: number;
  sd: number;
  low: number;
  high: number;
  note: string;
}

interface RawPayload {
  generated_at: string;
  equity_premium: number;
  inflation: number;
  inflation_month: string;
  assets: RawAssetEntry[];
}

export async function loadAssumptions(): Promise<AssumptionsData> {
  const res = await fetch("/data/assumptions.json");
  if (!res.ok) {
    throw new Error(`Could not load the model's numbers (status ${res.status})`);
  }
  const raw: RawPayload = await res.json();

  const assumptions = {} as Assumptions;
  const notes = {} as Record<Asset, string>;
  for (const asset of ASSETS) {
    const entry = raw.assets.find((a) => a.name === asset);
    if (!entry) {
      throw new Error(`The model's numbers file is missing "${asset}"`);
    }
    assumptions[asset as Asset] = {
      mean: entry.mean,
      sd: entry.sd,
      low: entry.low,
      high: entry.high,
    };
    notes[asset as Asset] = entry.note;
  }

  return {
    assumptions,
    notes,
    inflation: raw.inflation,
    inflationMonth: raw.inflation_month,
    generatedAt: raw.generated_at,
  };
}
