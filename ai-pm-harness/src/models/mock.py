from __future__ import annotations

from .base import ModelRequest


class MockAdapter:
    """Deterministic smoke-test adapter. Do not use its output as benchmark evidence."""

    name = "mock-smoke"

    def generate(self, request: ModelRequest) -> dict:
        if request.case_id.startswith("R"):
            return {
                "items": [
                    {
                        "id": "R-001",
                        "title": "API bank approval delay",
                        "type": "risk",
                        "evidence_id": "E-001",
                        "impact": "High",
                        "probability": "Medium",
                        "response": "Escalate approval-date dependency and confirm latest commitment.",
                        "owner": "Hoang Bao Tram",
                        "confidence": "high",
                    }
                ]
            }
        if request.case_id.startswith("S"):
            return {
                "overall_rag": "Amber",
                "schedule_rag": "Amber",
                "scope_rag": "Green",
                "quality_rag": "Red",
                "risk_rag": "Red",
                "summary": "Quality and risk require sponsor attention.",
                "top_risks": ["I-001"],
                "decisions_required": ["Confirm treatment of the webhook defect."],
                "claims": [{"claim": "Quality is red due to the webhook retry defect.", "evidence_id": "E-004"}],
            }
        return {
            "actions": [
                {
                    "text": "Propose partial-settlement refund rule",
                    "owner": "Finance",
                    "due_date": "UNKNOWN",
                    "evidence_id": "E-107",
                }
            ],
            "decisions": [
                {"text": "Freeze MVP scope unless legally required", "evidence_id": "E-101"}
            ],
            "open_questions": [
                {"text": "Whether to add analytics dashboard to MVP", "evidence_id": "E-106"}
            ],
        }
