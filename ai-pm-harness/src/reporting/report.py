from __future__ import annotations

import csv
from pathlib import Path


def summarize_benchmark(csv_path: str | Path) -> str:
    rows = list(csv.DictReader(Path(csv_path).open(encoding="utf-8")))
    if not rows:
        return "# Benchmark Report\n\nNo measured benchmark rows yet."

    models = sorted({row.get("model", "") for row in rows if row.get("model")})
    lines = ["# Benchmark Report", "", f"Measured rows: {len(rows)}", "", "Models: " + ", ".join(models)]
    lines += ["", "| Model | Use case | F1 | Unsupported claim rate | Leakage rate | Time saved |", "|---|---|---:|---:|---:|---:|"]
    for r in rows:
        lines.append(
            f"| {r.get('model','')} | {r.get('use_case','')} | {r.get('f1','')} | {r.get('unsupported_claim_rate','')} | {r.get('leakage_rate','')} | {r.get('time_saved_pct','')} |"
        )
    return "\n".join(lines) + "\n"
