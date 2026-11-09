// Port of src/model/simulate.py - keep these two files in sync if either changes.
//
// Takes a final split (from profile.ts) and an amount, and generates thousands
// of possible N-year futures, year by year, so we can show a real range of
// outcomes instead of one fake-precise number.
//
// Same assumption as the Python version, stated out loud: the investor
// RE-BALANCES back to their target split at the start of every year.
//
// Note on randomness: this uses its own small seeded random-number generator
// (not the same algorithm as NumPy's), so it will NOT produce bit-for-bit
// identical numbers to simulate.py for the same seed - only the same KIND of
// numbers, since both are 10,000-path Monte Carlo simulations of the same
// maths. We check that by comparing the simulated numbers to a known
// theoretical answer, the same way we checked the Python version.

import { ASSETS, type Asset, type Split } from "./profile";

export interface AssetAssumption {
  mean: number;
  sd: number;
  low: number;
  high: number;
}
export type Assumptions = Record<Asset, AssetAssumption>;

// Same modest, stated (not measured) correlation as simulate.py.
const UT_SHARE_CORRELATION = 0.15;

// A small seeded random generator so results are repeatable run to run
// (mulberry32 - simple, fast, good enough for this; not cryptographic).
function makeRng(seed: number) {
  let s = seed;
  return function uniform(): number {
    s |= 0;
    s = (s + 0x6d2b79f5) | 0;
    let t = Math.imul(s ^ (s >>> 15), 1 | s);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

// Box-Muller transform: turns two uniform [0,1) draws into one standard
// normal (mean 0, sd 1) draw - this is what produces the bell-curve shape.
function standardNormal(uniform: () => number): number {
  let u1 = 0;
  while (u1 === 0) u1 = uniform(); // avoid log(0)
  const u2 = uniform();
  return Math.sqrt(-2 * Math.log(u1)) * Math.cos(2 * Math.PI * u2);
}

function percentile(sortedAsc: Float64Array, p: number): number {
  const idx = (p / 100) * (sortedAsc.length - 1);
  const lo = Math.floor(idx);
  const hi = Math.ceil(idx);
  if (lo === hi) return sortedAsc[lo];
  const frac = idx - lo;
  return sortedAsc[lo] * (1 - frac) + sortedAsc[hi] * frac;
}

export interface SimulationResult {
  badCase: number; // 5th percentile
  middleCase: number; // 50th percentile (median)
  goodCase: number; // 95th percentile
  chanceOfLoss: number; // fraction of paths that ended below the starting amount
  chanceBeatsInflation: number; // fraction of paths that beat inflation
  inflationAdjustedTarget: number;
  inflationUsed: number;
}

export function simulate(
  finalSplit: Split,
  amount: number,
  years: number,
  inflation: number,
  assumptions: Assumptions,
  nPaths = 10_000,
  seed = 7
): SimulationResult {
  const uniform = makeRng(seed);

  const weights = ASSETS.map((a) => finalSplit[a] / 100);
  const mu = ASSETS.map((a) => assumptions[a].mean / 100);
  const sd = ASSETS.map((a) => assumptions[a].sd / 100);

  const iUt = ASSETS.indexOf("Unit trusts" as Asset);
  const iEq = ASSETS.indexOf("Shares (S&P SL20)" as Asset);
  const rho = UT_SHARE_CORRELATION;
  const sqrtOneMinusRhoSq = Math.sqrt(1 - rho * rho);

  const values = new Float64Array(nPaths).fill(amount);
  const z = new Array<number>(ASSETS.length);

  for (let y = 0; y < years; y++) {
    for (let p = 0; p < nPaths; p++) {
      // one independent standard-normal draw per asset
      for (let i = 0; i < ASSETS.length; i++) z[i] = standardNormal(uniform);

      // correlate Unit trusts <-> Shares only (everything else stays independent),
      // using the same two-variable trick Cholesky reduces to for one pair:
      // keep the first draw as-is, blend the second with it by rho.
      const zUt = z[iUt];
      z[iEq] = rho * zUt + sqrtOneMinusRhoSq * z[iEq];

      let portfolioReturn = 0;
      for (let i = 0; i < ASSETS.length; i++) {
        let r = mu[i] + sd[i] * z[i];
        if (r < -0.95) r = -0.95; // can't lose more than 95% in a year
        portfolioReturn += r * weights[i];
      }
      values[p] *= 1 + portfolioReturn;
    }
  }

  const sorted = Float64Array.from(values).sort();
  const inflationAdjustedTarget = amount * Math.pow(1 + inflation / 100, years);

  let lossCount = 0;
  let beatCount = 0;
  for (let p = 0; p < nPaths; p++) {
    if (values[p] < amount) lossCount++;
    if (values[p] > inflationAdjustedTarget) beatCount++;
  }

  return {
    badCase: percentile(sorted, 5),
    middleCase: percentile(sorted, 50),
    goodCase: percentile(sorted, 95),
    chanceOfLoss: lossCount / nPaths,
    chanceBeatsInflation: beatCount / nPaths,
    inflationAdjustedTarget,
    inflationUsed: inflation,
  };
}
