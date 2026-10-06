# AI-PM Harness for Fintech Project Operations

A controlled pilot for applying AI to practical project-management work in a fintech software project.

## Purpose

This repository is designed as a portfolio project for a Project Manager role that expects evidence of:

- practical AI/GenAI adoption in project management and software delivery;
- model/tool selection based on measurable criteria;
- harness engineering and output validation;
- hallucination / unsupported-claim control;
- confidentiality and data-sanitization controls;
- human-in-the-loop approval;
- measurement of productivity, quality and safety;
- usage guidance and team enablement.

The pilot uses **synthetic fintech project data only**. Replace the synthetic data with approved, anonymized data only after security review.

## Scope

Three PM use cases are implemented:

1. **Risk & Issue Analysis** - extract and structure risks/issues from RAID and project updates.
2. **Executive Status Report** - draft a structured project status summary from project evidence.
3. **Meeting -> Actions & Decisions** - turn meeting notes into actions, decisions and open questions.

The harness is model-agnostic. Model outputs can be imported from ChatGPT, Claude, Gemini or another approved model without exposing production data to this repository.

## Control philosophy

```text
Project data
    |
    v
Anonymization / sanitization
    |
    v
Task-specific prompt + schema + business rules
    |
    v
AI model
    |
    v
Structured output validator
    |
    +---- Evidence grounding check
    +---- Confidentiality check
    +---- Required-field check
    +---- Value / consistency check
    |
    v
Human review
    |
    v
Approved PM output
    |
    v
Evaluation log
```

## Repo map

```text
ai-pm-harness/
├── README.md
├── requirements.txt
├── docs/
│   ├── architecture.md
│   ├── methodology.md
│   ├── usage-guide.md
│   ├── training-slides.md
│   └── training-slides.pdf
├── data/
│   ├── raw/demo_project/
│   ├── anonymized/demo_project/
│   └── gold-standard/gold_cases.json
├── src/
│   ├── anonymizer/
│   ├── prompts/
│   ├── validators/
│   ├── evaluators/
│   ├── models/
│   └── reporting/
├── tests/
├── results/
└── demo/
    └── demo-script.md
```

## Quick start

Requires Python 3.11+.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 1) Anonymize the synthetic raw project package
python -m src.pipeline anonymize \
  --input data/raw/demo_project \
  --output data/anonymized/demo_project

# 2) Run the smoke-test validator against the included example output
python -m src.pipeline validate \
  --use-case risk \
  --input data/anonymized/demo_project/raid.csv \
  --output tests/fixtures/risk_output_example.json

# 3) Run tests
pytest -q
```

## How the benchmark works

The benchmark is intentionally separated from live model calls.

1. Prepare the same anonymized cases for each model.
2. Ask each model to return the exact JSON schema defined in `src/prompts/`.
3. Save the returned JSON under `results/model_outputs/<model_name>/<case_id>.json`.
4. Run validation and evaluation.
5. Record measured time and corrections in `results/benchmark.csv`.

This avoids hard-coding a vendor SDK and makes the methodology reproducible.

## Success metrics

Do not claim results before measurement. The target metrics are:

- task accuracy / F1 against a human-verified gold standard;
- unsupported factual claim rate;
- confidentiality leakage rate;
- median human correction time;
- time saved vs. a documented human baseline;
- model quality/cost trade-off;
- adoption / training completion.

## Important measurement rule

The repository contains **no fabricated performance claims**. Files under `results/` are templates until real benchmark runs are completed.

## Demo

The intended 3-5 minute demo flow is documented in `demo/demo-script.md`. The final `.mp4` should be a real screen recording of your own benchmark run; it is deliberately not fabricated in this starter repository.

## Portfolio outputs

After you run the pilot, attach these items to your application:

- Git repository / README;
- 3-4 page measured evaluation report;
- 3-5 minute demo video;
- usage guide + training slides;
- one CV bullet using only verified measured numbers.
