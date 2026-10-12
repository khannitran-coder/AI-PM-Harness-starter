"""Tests for the benchmark SCORER only. These use the gold labels as fake model output,
so they prove the scoring code works - they are NOT model results."""
import copy
import json

from src.evaluators import benchmark as bm


def _perfect_outputs(tmp_path, model="perfect"):
    folder = tmp_path / model
    folder.mkdir()
    for case in bm.load_cases():
        if case["category"] == bm.CONFIDENTIAL:
            continue
        payload = {k: v for k, v in case["gold"].items() if k != "expected_outcome"}
        (folder / f"{case['case_id']}.json").write_text(json.dumps(payload), encoding="utf-8")
    return folder


def test_perfect_output_scores_f1_one_and_no_unsupported(tmp_path):
    _perfect_outputs(tmp_path)
    rows = bm.score_model("perfect", bm.load_cases(), tmp_path, {})
    scored = [r for r in rows if r["category"] != bm.CONFIDENTIAL]
    assert len(scored) == 85
    assert all(r["f1"] == 1.0 for r in scored)
    assert all(r["unsupported_claim_rate"] == 0.0 for r in scored)


def test_invented_evidence_id_is_unsupported_and_blocked():
    case = next(c for c in bm.load_cases() if c["case_id"] == "R01")
    output = copy.deepcopy(case["gold"])
    output["items"].append({**output["items"][0], "id": "R-X", "evidence_id": "E-FAKE9"})
    row = bm.score_case(case, output)
    assert row["unsupported_claim_rate"] == 0.5
    assert row["f1"] < 1.0
    assert row["validation_status"] == "BLOCK"


def test_hallucination_trap_penalises_any_invented_item():
    case = next(c for c in bm.load_cases() if c["category"] == "hallucination-trap" and c["use_case"] == "risk")
    invented = {"items": [{"id": "R-1", "title": "x", "type": "risk", "evidence_id": next(iter(bm.evidence_ids(case["input_text"]))),
                           "impact": "High", "probability": "High", "response": "x", "owner": "UNKNOWN", "confidence": "low"}]}
    assert bm.score_case(case, invented)["unsupported_claim_rate"] == 1.0
    assert bm.score_case(case, {"items": []})["f1"] == 1.0


def test_status_rag_accuracy_counts_exact_matches():
    case = next(c for c in bm.load_cases() if c["case_id"] == "S01")
    output = copy.deepcopy(case["gold"])
    output["quality_rag"] = "Green"
    assert bm.score_case(case, output)["rag_accuracy"] == 0.8


def test_confidentiality_cases_are_blocked_at_gate_with_zero_leakage():
    rows = [bm.score_case(c, None) for c in bm.load_cases() if c["category"] == bm.CONFIDENTIAL]
    assert len(rows) == 5
    assert all(r["validation_status"] == "BLOCKED_AT_GATE" for r in rows)
    assert all(r["leakage_rate"] == 0.0 for r in rows)


def test_model_echoing_a_sensitive_token_counts_as_leakage():
    case = next(c for c in bm.load_cases() if c["category"] == bm.CONFIDENTIAL)
    token = sorted(bm.sensitive_tokens(case["input_text"]))[0]
    assert bm.score_case(case, {"items": [{"title": token}]})["leakage_rate"] > 0


def test_missing_and_invalid_outputs_are_handled(tmp_path):
    (tmp_path / "m").mkdir()
    (tmp_path / "m" / "R01.json").write_text("not json", encoding="utf-8")
    rows = bm.score_model("m", bm.load_cases(), tmp_path, {})
    r01 = next(r for r in rows if r["case_id"] == "R01")
    assert r01["f1"] == 0.0 and r01["validation_status"] == "BLOCK"
    assert not any(r["case_id"] == "R02" for r in rows)  # not run yet -> not counted


def test_parse_batch_accepts_fenced_answers():
    text = 'Here you go:\n```json\n{"R01": {"items": []}}\n```'
    assert bm.parse_batch(text) == {"R01": {"items": []}}
