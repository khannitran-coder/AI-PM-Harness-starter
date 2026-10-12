from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ClassificationMetrics:
    precision: float
    recall: float
    f1: float


def precision_recall_f1(predicted: set[str], expected: set[str]) -> ClassificationMetrics:
    tp = len(predicted & expected)
    fp = len(predicted - expected)
    fn = len(expected - predicted)
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0
    return ClassificationMetrics(precision, recall, f1)


def unsupported_claim_rate(unsupported: int, total: int) -> float:
    return unsupported / total if total else 0.0


def leakage_rate(leaked: int, sensitive_count: int) -> float:
    return leaked / sensitive_count if sensitive_count else 0.0


def time_saved_pct(baseline_minutes: float, assisted_minutes: float) -> float:
    if baseline_minutes <= 0:
        raise ValueError("baseline_minutes must be > 0")
    return (baseline_minutes - assisted_minutes) / baseline_minutes
