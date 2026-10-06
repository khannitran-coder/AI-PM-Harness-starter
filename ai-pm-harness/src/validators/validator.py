from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ALLOWED_RAG = {"Green", "Amber", "Red", "Unknown"}


def load_json(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def validate_risk_output(output: dict[str, Any], allowed_evidence: set[str], allowed_owners: set[str]) -> list[str]:
    errors: list[str] = []
    items = output.get("items")
    if not isinstance(items, list):
        return ["BLOCK: 'items' must be a list"]
    required = {"id", "title", "type", "evidence_id", "impact", "probability", "response", "owner", "confidence"}
    for idx, item in enumerate(items):
        missing = required - set(item)
        if missing:
            errors.append(f"BLOCK: item[{idx}] missing {sorted(missing)}")
        if item.get("evidence_id") not in allowed_evidence:
            errors.append(f"BLOCK: item[{idx}] unknown evidence_id={item.get('evidence_id')}")
        owner = item.get("owner")
        if owner not in allowed_owners and owner != "UNKNOWN":
            errors.append(f"WARN: item[{idx}] owner not in allowed owner set: {owner}")
        if item.get("confidence") not in {"low", "medium", "high"}:
            errors.append(f"WARN: item[{idx}] invalid confidence")
    return errors


def validate_status_output(output: dict[str, Any], allowed_evidence: set[str]) -> list[str]:
    errors: list[str] = []
    for key in ["overall_rag", "schedule_rag", "scope_rag", "quality_rag", "risk_rag"]:
        if output.get(key) not in ALLOWED_RAG:
            errors.append(f"BLOCK: invalid {key}={output.get(key)}")
    claims = output.get("claims", [])
    if not isinstance(claims, list):
        errors.append("BLOCK: claims must be a list")
    else:
        for idx, claim in enumerate(claims):
            if claim.get("evidence_id") not in allowed_evidence:
                errors.append(f"BLOCK: claim[{idx}] unsupported evidence_id={claim.get('evidence_id')}")
    return errors


def validate_meeting_output(output: dict[str, Any], allowed_evidence: set[str]) -> list[str]:
    errors: list[str] = []
    for collection_name in ["actions", "decisions", "open_questions"]:
        if not isinstance(output.get(collection_name), list):
            errors.append(f"BLOCK: {collection_name} must be a list")
    for collection_name in ["actions", "decisions", "open_questions"]:
        for idx, item in enumerate(output.get(collection_name, [])):
            if item.get("evidence_id") not in allowed_evidence:
                errors.append(f"BLOCK: {collection_name}[{idx}] unknown evidence_id={item.get('evidence_id')}")
            if collection_name == "actions" and item.get("due_date") in {None, ""}:
                errors.append(f"WARN: actions[{idx}] due_date missing; use UNKNOWN when not stated")
    return errors


def validate(use_case: str, output: dict[str, Any], allowed_evidence: set[str], allowed_owners: set[str] | None = None) -> list[str]:
    allowed_owners = allowed_owners or set()
    if use_case == "risk":
        return validate_risk_output(output, allowed_evidence, allowed_owners)
    if use_case == "status":
        return validate_status_output(output, allowed_evidence)
    if use_case == "meeting":
        return validate_meeting_output(output, allowed_evidence)
    return [f"BLOCK: unsupported use case={use_case}"]
