from __future__ import annotations

import re
from pathlib import Path

REPLACEMENTS = {
    "Nguyen Minh Anh": "USER_001",
    "Le Thu Ha": "USER_002",
    "Pham Duc Long": "USER_003",
    "Hoang Bao Tram": "USER_004",
    "Tran Khai Chi": "USER_005",
    "CloudBridge Labs": "VENDOR_001",
}

PATTERNS = [
    (re.compile(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}"), "[EMAIL_REDACTED]"),
    (re.compile(r"\+?\d[\d\s-]{8,}\d"), "[PHONE_REDACTED]"),
    (re.compile(r"\b\d{4}(?:[ -]?\d{4}){3}\b"), "[ACCOUNT_REDACTED]"),
    (re.compile(r"\bsk_demo_[A-Za-z0-9_-]+\b"), "[SECRET_REDACTED]"),
]


def anonymize_text(text: str) -> str:
    result = text
    for source, target in REPLACEMENTS.items():
        result = result.replace(source, target)
    for pattern, replacement in PATTERNS:
        result = pattern.sub(replacement, result)
    return result


def anonymize_directory(input_dir: str | Path, output_dir: str | Path) -> None:
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    for src in input_path.rglob("*"):
        if not src.is_file():
            continue
        rel = src.relative_to(input_path)
        dst = output_path / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        text = src.read_text(encoding="utf-8")
        dst.write_text(anonymize_text(text), encoding="utf-8")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    anonymize_directory(args.input, args.output)
    print(f"Anonymized: {args.input} -> {args.output}")
