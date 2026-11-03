"""
Run the whole data pipeline, in order, with one command.
If any step fails, it stops and says which one, so bad data never moves on.

    python src/data/run_pipeline.py
"""

import subprocess
import sys

STEPS = [
    ("Pull S&P SL20 snapshot",      "src/data/cse_pull.py"),
    ("Pull history for all stocks", "src/data/cse_history_all.py"),
    ("Pull CBSL monthly rates",      "src/data/cbsl_rates_pull.py"),
    ("Combine into one price table", "src/data/clean_cse_prices.py"),
    ("Find and fix price anomalies", "src/data/check_jumps.py"),
    ("Make model inputs + quality",  "src/data/make_model_inputs.py"),
]

for name, script in STEPS:
    print(f"\n=== {name} ({script}) ===")
    result = subprocess.run([sys.executable, script])
    if result.returncode != 0:
        print(f"\nSTOPPED: '{name}' failed. Later steps were not run.")
        sys.exit(1)

print("\nPipeline finished.")
