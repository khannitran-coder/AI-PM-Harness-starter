# Results

This folder deliberately starts without fabricated benchmark numbers.

## Files produced by a benchmark run

- `model_outputs/<model>/<case_id>.json` - raw model answers (created by `benchmark split`).
- `timing.csv` - manual stopwatch measurements (columns: `model,use_case,case_id,baseline_minutes,assisted_minutes,correction_count`). Leave `model` empty for a baseline that applies to every model.
- `benchmark.csv` - one row per scored case (written by `benchmark score`).
- `summary.md` - per-model and per-category summary (written by `benchmark score`).
- `evaluation-report.md` - the narrative report, written by a human after reading `summary.md`.

## `benchmark.csv` columns

`model, use_case, case_id, category, f1, rag_accuracy, unsupported_claim_rate, leakage_rate, validation_status, baseline_minutes, assisted_minutes, time_saved_pct, correction_count, notes`

Do not convert a target into a result.
