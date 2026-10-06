from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.anonymizer.anonymizer import anonymize_directory
from src.validators.validator import load_json, validate


def extract_evidence_ids(text: str) -> set[str]:
    import re
    return set(re.findall(r"E-\d+", text))


def command_validate(use_case: str, input_path: str, output_path: str) -> int:
    source = Path(input_path).read_text(encoding="utf-8")
    allowed_evidence = extract_evidence_ids(source)
    if use_case == "risk":
        import csv
        with open(input_path, encoding="utf-8") as f:
            allowed_owners = {r["owner"] for r in csv.DictReader(f) if r.get("owner")}
    else:
        allowed_owners = set()
    output = load_json(output_path)
    errors = validate(use_case, output, allowed_evidence, allowed_owners)
    if errors:
        print("\n".join(errors))
        return 1 if any(x.startswith("BLOCK") for x in errors) else 0
    print("PASS: output passed structural and evidence-reference checks")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="AI-PM Harness CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    p1 = sub.add_parser("anonymize")
    p1.add_argument("--input", required=True)
    p1.add_argument("--output", required=True)

    p2 = sub.add_parser("validate")
    p2.add_argument("--use-case", choices=["risk", "status", "meeting"], required=True)
    p2.add_argument("--input", required=True)
    p2.add_argument("--output", required=True)

    args = parser.parse_args()
    if args.command == "anonymize":
        anonymize_directory(args.input, args.output)
        print(f"Anonymized {args.input} -> {args.output}")
        return 0
    return command_validate(args.use_case, args.input, args.output)


if __name__ == "__main__":
    raise SystemExit(main())
