from src.anonymizer.anonymizer import anonymize_text


def test_anonymize_email_phone_account_secret():
    raw = "Nguyen Minh Anh <minh.anh@example.test> +84 912 345 678 9704 1234 5678 9012 sk_demo_not_real_ABC123XYZ"
    cleaned = anonymize_text(raw)
    assert "minh.anh@example.test" not in cleaned
    assert "+84 912 345 678" not in cleaned
    assert "9704 1234 5678 9012" not in cleaned
    assert "sk_demo_not_real_ABC123XYZ" not in cleaned
    assert "USER_001" in cleaned
    assert "[EMAIL_REDACTED]" in cleaned


def test_anonymize_directory(tmp_path):
    src = tmp_path / "in"
    dst = tmp_path / "out"
    src.mkdir()
    (src / "a.txt").write_text("CloudBridge Labs", encoding="utf-8")
    from src.anonymizer.anonymizer import anonymize_directory
    anonymize_directory(src, dst)
    assert (dst / "a.txt").read_text(encoding="utf-8") == "VENDOR_001"
