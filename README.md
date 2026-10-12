# AI-PM Harness

[![CI](https://github.com/khannitran-coder/ai-pm-harness-starter/actions/workflows/main.yml/badge.svg)](https://github.com/khannitran-coder/ai-pm-harness-starter/actions/workflows/main.yml)
![Python](https://img.shields.io/badge/python-3.11%2B-blue)

A controlled pilot for using AI on three project-management tasks in a fintech software project, with a validation harness around the model:

1. **Risk & issue analysis** - structure risks and issues from a RAID log and project updates.
2. **Executive status report** - draft a RAG status summary from project evidence.
3. **Meeting notes to actions & decisions** - extract actions, decisions and open questions.

The model is never trusted to decide. Input is anonymized first, output must be structured JSON, every claim must cite evidence, unsupported or confidential content is flagged (PASS / WARN / BLOCK), and a human approves the final result. The harness is model-agnostic: outputs from ChatGPT, Claude, Gemini or any approved model are pasted in as JSON, so no vendor SDK or API key is needed.

## Status

| Component | Status |
|---|---|
| Anonymizer (email, phone, account, demo secrets, names) | Implemented, unit-tested |
| Output validator (PASS / WARN / BLOCK) for the 3 use cases | Implemented, unit-tested |
| Metrics (precision / recall / F1, unsupported-claim rate, leakage rate, time saved) | Implemented, unit-tested |
| 90-case gold set (6 categories, synthetic data) | Built and structurally tested; single reviewer |
| Benchmark runner (`prompts` / `split` / `score`) | Implemented; tested with the gold set as fake output (scorer tests only) |
| **Measured results with real models** | **Not run yet** - `results/benchmark.csv` is empty on purpose |
| Live model API adapters | Not built (outputs are pasted in as JSON) |

No performance numbers are claimed anywhere in this repository until they appear in `results/benchmark.csv`. All project data is synthetic.

## How it works

```text
Project data
    -> Anonymization / sanitization
    -> Task-specific prompt + JSON schema + business rules
    -> AI model (any, output pasted in)
    -> Validator: evidence grounding | confidentiality | required fields | value consistency
    -> Human review
    -> Approved PM output
    -> Evaluation log
```

Design details: [architecture](./docs/architecture.md) · [methodology](./docs/methodology.md) · [usage guide](./docs/usage-guide.md) · [training slides](./docs/training-slides.pdf).

## Quick start

Requires Python 3.11+.

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pytest -q

# anonymize the synthetic raw project package
python -m src.pipeline anonymize \
  --input data/raw/demo_project \
  --output data/anonymized/demo_project

# validate the included example model output against the anonymized RAID log
python -m src.pipeline validate \
  --use-case risk \
  --input data/anonymized/demo_project/raid.csv \
  --output tests/fixtures/risk_output_example.json
```

A one-command check of the synthetic flow (also run in CI): `python -m scripts.verify_demo`.

## Benchmark

The benchmark is separated from live model calls: the 90-case gold set is fixed first, so scoring cannot be tuned after seeing results.

```bash
# 1) build one batch prompt per use case (inputs are anonymized)
python -m src.evaluators.benchmark prompts --use-case risk      # also: status, meeting

# 2) paste results/prompts/risk.md into the model, save the answer to a file, then split it
python -m src.evaluators.benchmark split --model <model-name> --use-case risk --input answer.txt

# 3) score every model found under results/model_outputs/
python -m src.evaluators.benchmark score
```

`score` writes `results/benchmark.csv` (one row per case) and `results/summary.md`. Step-by-step instructions, including the human-baseline timing protocol, are in the [benchmark runbook](./docs/benchmark-runbook.md).

The scorer is mechanical and strict: evidence-level F1 against the gold set, RAG-field accuracy for status reports, unsupported references (evidence ids not present in the case input, or content invented in hallucination traps), sensitive-token leakage, and PASS/WARN/BLOCK validation. It does **not** judge the quality of free-text fields; that requires human review.

Target metrics: accuracy / F1 against the gold set, unsupported-claim rate, confidentiality leakage rate, median human correction time, time saved versus a documented human baseline, and model quality/cost trade-off.

## Repository layout

```text
src/           anonymizer · prompts · validators · evaluators (metrics + benchmark) · models · reporting · pipeline
data/          raw/ and anonymized/ synthetic project data · gold-standard/ (90 cases)
tests/         unit tests for every component
docs/          architecture · methodology · usage guide · benchmark runbook · training slides
results/       benchmark outputs and evaluation report (templates until measured)
demo/          3-5 minute demo script
scripts/       verify_demo.py (synthetic end-to-end check used in CI)
```

## Next steps

- Run the benchmark with at least two models following the runbook, and fill in `results/evaluation-report.md` from the measured numbers.
- Record a short demo of a real benchmark run (script in [`demo/demo-script.md`](./demo/demo-script.md)).

Related project: [Sprint Risk Monitoring Agent](https://github.com/khannitran-coder/risk-monitoring-agent-2.0) - a LangGraph agent that applies the same principle (rules decide, the model drafts, a human approves).

## Data note

All data in this repository is synthetic, including the intentionally fake "sensitive" values in `data/raw/demo_project/sensitive_demo.txt` that exist to test the anonymizer. Do not commit real project data, credentials or personal information.
