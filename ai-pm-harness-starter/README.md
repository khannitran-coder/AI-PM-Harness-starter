# AI-PM Harness

[![CI](https://github.com/khannitran-coder/ai-pm-harness-starter/actions/workflows/ci.yml/badge.svg)](https://github.com/khannitran-coder/ai-pm-harness-starter/actions/workflows/ci.yml)

A controlled pilot for using AI on three project-management tasks - **risk analysis (RAID)**, **executive status reports** and **meeting notes to actions/decisions** - with a validation harness around the model: anonymization, evidence-grounding checks, PASS/WARN/BLOCK validation, human review and a measurable benchmark.

The model is never trusted to decide. Output must be structured JSON, every claim must cite evidence, unsupported content is flagged, and a human approves the final result.

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

No performance numbers are claimed anywhere in this repository until they appear in `results/benchmark.csv`.

## Quick start

```bash
cd ai-pm-harness
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pytest -q
```

Then follow [`ai-pm-harness/docs/benchmark-runbook.md`](ai-pm-harness/docs/benchmark-runbook.md) to run the benchmark, or read [`ai-pm-harness/README.md`](ai-pm-harness/README.md) for the full design and methodology.

## Repository layout

```text
ai-pm-harness/
├── src/           anonymizer, prompts, validators, evaluators (metrics + benchmark runner)
├── data/          synthetic project data and the 90-case gold standard
├── tests/         unit tests for every component
├── docs/          architecture, methodology, usage guide, benchmark runbook, training slides
└── results/       benchmark outputs (empty until measured)
```

Related project: [Sprint Risk Monitoring Agent](https://github.com/khannitran-coder/risk-monitoring-agent-2.0) - a LangGraph agent that applies the same principle (rules decide, the model drafts, a human approves).

## Data note

All data in this repository is synthetic. Do not commit real project data, credentials or personal information.
