from src.validators.validator import validate


def test_valid_risk_output_passes():
    output = {
        "items": [{
            "id": "R-001", "title": "x", "type": "risk", "evidence_id": "E-001",
            "impact": "High", "probability": "Medium", "response": "x",
            "owner": "Hoang Bao Tram", "confidence": "high"
        }]
    }
    errors = validate("risk", output, {"E-001"}, {"Hoang Bao Tram"})
    assert not errors


def test_unknown_evidence_blocks():
    output = {
        "items": [{
            "id": "R-001", "title": "x", "type": "risk", "evidence_id": "E-999",
            "impact": "High", "probability": "Medium", "response": "x",
            "owner": "Hoang Bao Tram", "confidence": "high"
        }]
    }
    errors = validate("risk", output, {"E-001"}, {"Hoang Bao Tram"})
    assert any(e.startswith("BLOCK") for e in errors)
