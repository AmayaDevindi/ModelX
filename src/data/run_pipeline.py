"""
Run the whole data pipeline, in order, with one command.

    python src/data/run_pipeline.py

Each step is either:
  required (True)  - if it fails, the pipeline stops, so bad data never moves on.
  optional (False) - if it fails (site down, or it blocks cloud computers like
                     GitHub's), we warn, keep the last good file and carry on.
Skipped optional steps are listed at the end so nothing is hidden.
"""

import subprocess
import sys

STEPS = [
    # name,                          script,                              required?
    ("Pull S&P SL20 snapshot",       "src/data/cse_pull.py",              True),
    ("Pull history for all stocks",  "src/data/cse_history_all.py",       True),
    ("Pull CBSL monthly rates",      "src/data/cbsl_rates_pull.py",       False),
    ("Pull CBSL inflation (CCPI)",   "src/data/cbsl_ccpi_pull.py",        False),
    ("Pull CBSL weekly yields (PDF)", "src/data/cbsl_weekly_pull.py",     False),
    ("Pull UTASL unit trust prices", "src/data/utasl_pull.py",            False),
    ("Pull UTASL fund performance",  "src/data/utasl_performance_pull.py", False),
    ("Pull CBSL USD/LKR rate",       "src/data/cbsl_fx_pull.py",          False),
    ("Pull news headlines",          "src/data/news_pull.py",             False),
    ("Combine into one price table", "src/data/clean_cse_prices.py",      True),
    ("Find and fix price anomalies", "src/data/check_jumps.py",           True),
    ("Make model inputs + quality",  "src/data/make_model_inputs.py",     True),
    ("Export model numbers for the website", "src/data/export_model_json.py", True),
]

skipped = []

for name, script, required in STEPS:
    print(f"\n=== {name} ({script}) ===")
    result = subprocess.run([sys.executable, script])
    if result.returncode != 0:
        if required:
            print(f"\nSTOPPED: '{name}' failed. Later steps were not run.")
            sys.exit(1)
        print(f"\nWARNING: '{name}' failed. Keeping the last good file and carrying on.")
        skipped.append(name)

print("\nPipeline finished.")
if skipped:
    print("Skipped (data for these was NOT refreshed this run):")
    for name in skipped:
        print("  -", name)
