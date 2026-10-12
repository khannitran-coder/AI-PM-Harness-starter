"""Synthetic demo verification; not a live LLM evaluation."""
from pathlib import Path
from tempfile import TemporaryDirectory
from src.anonymizer.anonymizer import anonymize_directory
from src.pipeline import command_validate

ROOT = Path(__file__).resolve().parents[1]

def main():
    with TemporaryDirectory() as d:
        anonymize_directory(str(ROOT / "data/raw/demo_project"), d)
        assert any(Path(d).rglob("*")), "Anonymization produced no files"
        print("PASS: anonymization produced output files")
    code = command_validate(
        "risk",
        str(ROOT / "data/anonymized/demo_project/raid.csv"),
        str(ROOT / "tests/fixtures/risk_output_example.json"),
    )
    assert code == 0, "Risk validator blocked the sample"
    print("DEMO VERIFIED: synthetic anonymization and risk validation; no LLM benchmark performed")

if __name__ == "__main__":
    main()
