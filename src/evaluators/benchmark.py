"""Benchmark runner for the 90-case gold set.

Three sub-commands (no vendor SDK needed - model outputs are pasted in as JSON):

    python -m src.evaluators.benchmark prompts --use-case risk
    python -m src.evaluators.benchmark split   --model my-model --use-case risk --input answer.txt
    python -m src.evaluators.benchmark score

Scoring is deliberately strict and mechanical. It measures evidence-level
agreement with the gold set, unsupported references, and sensitive-token leakage.
It does NOT judge the semantic quality of free text; that needs human review.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import statistics
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

from src.anonymizer.anonymizer import PATTERNS, REPLACEMENTS, anonymize_text
from src.evaluators.metrics import precision_recall_f1, time_saved_pct
from src.validators.validator import validate

ROOT = Path(__file__).resolve().parents[2]
GOLD_PATH = ROOT / "data" / "gold-standard" / "gold_cases.json"
PROMPT_DIR = ROOT / "src" / "prompts"
RESULTS_DIR = ROOT / "results"
OUTPUT_DIR = RESULTS_DIR / "model_outputs"

PROMPT_FILES = {
    "risk": "risk_analysis.txt",
    "status": "status_report.txt",
    "meeting": "meeting_to_actions.txt",
}
COLLECTIONS = {
    "risk": ["items"],
    "status": ["claims"],
    "meeting": ["actions", "decisions", "open_questions"],
}
RAG_FIELDS = ["overall_rag", "schedule_rag", "scope_rag", "quality_rag", "risk_rag"]
EVIDENCE_RE = re.compile(r"E-[A-Za-z]*\d+")
CONFIDENTIAL = "confidentiality-trap"
CSV_COLUMNS = [
    "model", "use_case", "case_id", "category", "f1", "rag_accuracy",
    "unsupported_claim_rate", "leakage_rate", "validation_status",
    "baseline_minutes", "assisted_minutes", "time_saved_pct", "correction_count", "notes",
]


# ----------------------------------------------------------------- helpers
def load_cases(path: Path = GOLD_PATH) -> list[dict[str, Any]]:
    return json.loads(path.read_text(encoding="utf-8"))


def evidence_ids(text: str) -> set[str]:
    return set(EVIDENCE_RE.findall(text))


def sensitive_tokens(text: str) -> set[str]:
    """Sensitive strings present in raw text (emails, phones, accounts, demo keys, known names)."""
    found: set[str] = set()
    for pattern, _ in PATTERNS:
        found.update(m.group(0) for m in pattern.finditer(text))
    found.update(name for name in REPLACEMENTS if name in text)
    return found


def _items(use_case: str, payload: dict[str, Any]) -> list[tuple[str, dict[str, Any]]]:
    out: list[tuple[str, dict[str, Any]]] = []
    for coll in COLLECTIONS[use_case]:
        value = payload.get(coll)
        if isinstance(value, list):
            out.extend((coll, i) for i in value if isinstance(i, dict))
    return out


def _keys(use_case: str, payload: dict[str, Any]) -> set[str]:
    return {f"{coll}:{i.get('evidence_id')}" for coll, i in _items(use_case, payload)}


def _status(errors: list[str]) -> str:
    if any(e.startswith("BLOCK") for e in errors):
        return "BLOCK"
    return "WARN" if any(e.startswith("WARN") for e in errors) else "PASS"


# ----------------------------------------------------------------- scoring
def score_case(case: dict[str, Any], output: dict[str, Any] | None, note: str = "") -> dict[str, Any]:
    use_case, category = case["use_case"], case["category"]
    row: dict[str, Any] = {c: "" for c in CSV_COLUMNS}
    row.update(use_case=use_case, case_id=case["case_id"], category=category, notes=note)

    tokens = sensitive_tokens(case["input_text"])
    if category == CONFIDENTIAL:
        leaked = {t for t in tokens if t in anonymize_text(case["input_text"])}
        if output is not None:
            blob = json.dumps(output, ensure_ascii=False)
            leaked |= {t for t in tokens if t in blob}
        row["leakage_rate"] = round(len(leaked) / len(tokens), 4) if tokens else ""
        row["validation_status"] = "BLOCKED_AT_GATE" if tokens else "GATE_MISS"
        return row

    if output is None:
        row["validation_status"] = "BLOCK"
        row["f1"] = 0.0
        row["notes"] = note or "no usable output"
        return row

    pred, gold = _keys(use_case, output), _keys(use_case, case["gold"])
    row["f1"] = 1.0 if not pred and not gold else round(precision_recall_f1(pred, gold).f1, 4)

    if use_case == "status":
        hits = sum(1 for f in RAG_FIELDS if output.get(f) == case["gold"].get(f))
        row["rag_accuracy"] = round(hits / len(RAG_FIELDS), 4)

    allowed = evidence_ids(case["input_text"])
    gold_empty = {c for c in COLLECTIONS[use_case] if not case["gold"].get(c)}
    predicted = _items(use_case, output)
    unsupported = 0
    for coll, item in predicted:
        invented = category == "hallucination-trap" and coll in gold_empty
        if item.get("evidence_id") not in allowed or invented:
            unsupported += 1
    row["unsupported_claim_rate"] = round(unsupported / len(predicted), 4) if predicted else 0.0

    owners = {i.get("owner") for i in case["gold"].get("items", []) if isinstance(i, dict)}
    owners |= set(REPLACEMENTS.values())
    try:
        row["validation_status"] = _status(validate(use_case, output, allowed, owners))
    except (AttributeError, TypeError):
        row["validation_status"] = "BLOCK"
        row["notes"] = (note + " malformed output").strip()
    return row


def load_output(model_dir: Path, case_id: str) -> tuple[dict[str, Any] | None, str]:
    path = model_dir / f"{case_id}.json"
    if not path.exists():
        return None, "missing output file"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None, "invalid JSON"
    return (data, "") if isinstance(data, dict) else (None, "output is not a JSON object")


def load_timing(path: Path) -> dict[tuple[str, str], dict[str, str]]:
    if not path.exists():
        return {}
    with path.open(encoding="utf-8", newline="") as f:
        return {((r.get("model") or "*").strip() or "*", r["case_id"].strip()): r for r in csv.DictReader(f)}


def score_model(model: str, cases: list[dict[str, Any]], output_dir: Path,
                timing: dict[tuple[str, str], dict[str, str]]) -> list[dict[str, Any]]:
    rows = []
    for case in cases:
        output, note = load_output(output_dir / model, case["case_id"])
        if note == "missing output file" and case["category"] != CONFIDENTIAL:
            continue  # not run yet: do not count as a failure
        row = score_case(case, output, note)
        row["model"] = model
        t = timing.get((model, case["case_id"])) or timing.get(("*", case["case_id"]))
        if t and t.get("baseline_minutes") and t.get("assisted_minutes"):
            base, assisted = float(t["baseline_minutes"]), float(t["assisted_minutes"])
            row.update(baseline_minutes=base, assisted_minutes=assisted,
                       time_saved_pct=round(time_saved_pct(base, assisted) * 100, 1),
                       correction_count=t.get("correction_count", ""))
        rows.append(row)
    return rows


# ----------------------------------------------------------------- reporting
def _mean(rows: list[dict[str, Any]], col: str) -> str:
    vals = [float(r[col]) for r in rows if r[col] != ""]
    return f"{statistics.mean(vals):.3f}" if vals else "n/a"


def _median(rows: list[dict[str, Any]], col: str) -> str:
    vals = [float(r[col]) for r in rows if r[col] != ""]
    return f"{statistics.median(vals):.1f}%" if vals else "n/a"


def summarize(rows: list[dict[str, Any]]) -> str:
    lines = ["# Benchmark summary (auto-generated by `benchmark score`)", "",
             "Strict, mechanical scoring only. Semantic quality needs human review. "
             "Gold labels are synthetic and single-reviewer.", ""]
    for model in sorted({r["model"] for r in rows}):
        mr = [r for r in rows if r["model"] == model]
        lines += [f"## {model}", "", "| Use case | n | mean F1 | RAG accuracy | unsupported claim rate | BLOCK | WARN | median time saved |",
                  "|---|---:|---:|---:|---:|---:|---:|---:|"]
        for uc in ("risk", "status", "meeting"):
            ur = [r for r in mr if r["use_case"] == uc and r["category"] != CONFIDENTIAL]
            if not ur:
                continue
            lines.append(f"| {uc} | {len(ur)} | {_mean(ur, 'f1')} | {_mean(ur, 'rag_accuracy')} | "
                         f"{_mean(ur, 'unsupported_claim_rate')} | "
                         f"{sum(r['validation_status'] == 'BLOCK' for r in ur)} | "
                         f"{sum(r['validation_status'] == 'WARN' for r in ur)} | {_median(ur, 'time_saved_pct')} |")
        lines += ["", "| Category | n | mean F1 | unsupported claim rate |", "|---|---:|---:|---:|"]
        for cat in sorted({r["category"] for r in mr if r["category"] != CONFIDENTIAL}):
            cr = [r for r in mr if r["category"] == cat]
            lines.append(f"| {cat} | {len(cr)} | {_mean(cr, 'f1')} | {_mean(cr, 'unsupported_claim_rate')} |")
        cr = [r for r in mr if r["category"] == CONFIDENTIAL]
        if cr:
            lines += ["", f"Confidentiality traps: {len(cr)} cases, leakage rate {_mean(cr, 'leakage_rate')}, "
                      f"gate blocked {sum(r['validation_status'] == 'BLOCKED_AT_GATE' for r in cr)}/{len(cr)}."]
        lines.append("")
    return "\n".join(lines)


# ----------------------------------------------------------------- commands
def cmd_prompts(use_case: str) -> int:
    template = (PROMPT_DIR / PROMPT_FILES[use_case]).read_text(encoding="utf-8").strip()
    cases = [c for c in load_cases() if c["use_case"] == use_case and c["category"] != CONFIDENTIAL]
    parts = [template, "", "---", "BATCH INSTRUCTIONS",
             "Process every case below independently, as if it were a separate request. Do not carry facts between cases.",
             'Return ONE JSON object whose keys are the case ids and whose values follow the SCHEMA above, '
             'e.g. {"' + cases[0]["case_id"] + '": {...}, "' + cases[1]["case_id"] + '": {...}}.',
             "JSON only: no markdown fences, no commentary.", "---", ""]
    for c in cases:
        parts += [f"CASE {c['case_id']}", anonymize_text(c["input_text"]), ""]
    out = RESULTS_DIR / "prompts" / f"{use_case}.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(parts), encoding="utf-8")
    print(f"Wrote {out} ({len(cases)} cases; confidentiality traps are excluded and tested at the gate).")
    return 0


def parse_batch(text: str) -> dict[str, Any]:
    start, end = text.find("{"), text.rfind("}")
    if start < 0 or end <= start:
        raise ValueError("no JSON object found in the pasted answer")
    data = json.loads(text[start:end + 1])
    if not isinstance(data, dict):
        raise ValueError("expected a JSON object keyed by case id")
    return data


def cmd_split(model: str, use_case: str, input_path: Path) -> int:
    expected = {c["case_id"] for c in load_cases() if c["use_case"] == use_case and c["category"] != CONFIDENTIAL}
    try:
        data = parse_batch(input_path.read_text(encoding="utf-8"))
    except (ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    target = OUTPUT_DIR / model
    target.mkdir(parents=True, exist_ok=True)
    written = 0
    for case_id, payload in data.items():
        if case_id in expected and isinstance(payload, dict):
            (target / f"{case_id}.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
            written += 1
    print(f"Wrote {written} files to {target}")
    missing, extra = sorted(expected - set(data)), sorted(set(data) - expected)
    if missing:
        print(f"Missing from the answer: {', '.join(missing)}")
    if extra:
        print(f"Ignored unknown ids: {', '.join(extra)}")
    return 0


def cmd_score(models: list[str] | None) -> int:
    if not models:
        models = sorted(p.name for p in OUTPUT_DIR.iterdir() if p.is_dir()) if OUTPUT_DIR.exists() else []
    if not models:
        print("No model outputs found under results/model_outputs/<model>/. Run `prompts` and `split` first.", file=sys.stderr)
        return 1
    cases, timing = load_cases(), load_timing(RESULTS_DIR / "timing.csv")
    rows: list[dict[str, Any]] = []
    for m in models:
        rows.extend(score_model(m, cases, OUTPUT_DIR, timing))
    RESULTS_DIR.mkdir(exist_ok=True)
    with (RESULTS_DIR / "benchmark.csv").open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    summary = summarize(rows)
    (RESULTS_DIR / "summary.md").write_text(summary, encoding="utf-8")
    print(summary)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="AI-PM Harness benchmark runner")
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("prompts", help="build one batch prompt per use case")
    p.add_argument("--use-case", choices=list(PROMPT_FILES), required=True)
    s = sub.add_parser("split", help="split a pasted batch answer into per-case JSON files")
    s.add_argument("--model", required=True)
    s.add_argument("--use-case", choices=list(PROMPT_FILES), required=True)
    s.add_argument("--input", required=True, type=Path)
    sc = sub.add_parser("score", help="score all models and write results/benchmark.csv + summary.md")
    sc.add_argument("--models", nargs="*")
    args = parser.parse_args()
    if args.command == "prompts":
        return cmd_prompts(args.use_case)
    if args.command == "split":
        return cmd_split(args.model, args.use_case, args.input)
    return cmd_score(args.models)


if __name__ == "__main__":
    raise SystemExit(main())
