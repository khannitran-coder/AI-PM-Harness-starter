# Benchmark runbook

Goal: produce real, reproducible numbers for 2+ models without any API integration.
Use only the synthetic data in this repository. Never paste real project data into a model.

## 0. Setup

```bash
cd ai-pm-harness
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pytest -q          # everything must be green before you measure anything
```

GitHub Codespaces works fine (open the repo -> Code -> Codespaces).

## 1. Fix the protocol before you look at results

Write down in `results/evaluation-report.md`: model names **and versions**, date, whether web/search/memory tools are off, and that the gold set will not be edited after the first run. If you find a gold-label error, fix it, record it in the report, and re-run **all** models.

## 2. Build the prompts

```bash
python -m src.evaluators.benchmark prompts --use-case risk
python -m src.evaluators.benchmark prompts --use-case status
python -m src.evaluators.benchmark prompts --use-case meeting
```

This creates `results/prompts/<use_case>.md` (28 / 28 / 29 cases). Inputs are anonymized. The 5 confidentiality traps are not sent to a model: they test the sanitizer gate.

## 3. Run each model

For each model and each use case: open a **new chat**, paste the whole prompt file, and save the answer to a text file. Markdown fences around the JSON are fine. Then:

```bash
python -m src.evaluators.benchmark split --model chatgpt-<version> --use-case risk --input answer_risk.txt
```

Check the "Missing from the answer" line. If a model skipped cases, ask it once to continue with only those ids and split again; record this in the report. Cases batched into one chat can influence each other: state this as a limitation, or re-run a sample of cases one per chat.

## 4. Measure time saved (human baseline)

Pick 5 cases per use case. Do each **by hand** with a stopwatch (baseline), then do the same case with the AI output, reviewing and correcting it (assisted). Record both in `results/timing.csv`:

```csv
model,use_case,case_id,baseline_minutes,assisted_minutes,correction_count
,risk,R03,6.0,,
chatgpt-<version>,risk,R03,,2.5,1
```

Use one row for the baseline (empty model) and one per model for the assisted time, or put both numbers in the same row.

## 5. Score

```bash
python -m src.evaluators.benchmark score
```

Read `results/summary.md`. Look at the worst cases in `results/benchmark.csv` (sort by `f1` and `unsupported_claim_rate`) and open the matching `model_outputs` file to understand why.

## 6. Human review (required before claiming anything)

Review at least 10 low-scoring cases by hand. For each, decide whether the model or the gold label is wrong. Put 3 examples in the report: one correct extraction, one hallucination caught by the validator, one case where the gold label was debatable.

## 7. Report and commit

Fill `results/evaluation-report.md` with measured numbers only. State: synthetic data, single run, single reviewer, strict evidence-level matching, small sample. Commit `results/benchmark.csv`, `results/summary.md`, `results/model_outputs/` and the report in separate commits with clear messages.

## Rules

- No number goes into a CV or README unless it is in `benchmark.csv`.
- Never edit gold labels to improve a score.
- A bad result honestly explained is better evidence than a perfect one.
