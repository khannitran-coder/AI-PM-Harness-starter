import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GOLD = ROOT / 'data' / 'gold-standard' / 'gold_cases.json'


def load_cases():
    return json.loads(GOLD.read_text(encoding='utf-8'))


def test_gold_set_has_90_unique_cases():
    cases = load_cases()
    assert len(cases) == 90
    assert len({c['case_id'] for c in cases}) == 90


def test_gold_set_category_distribution():
    counts = Counter(c['category'] for c in load_cases())
    assert counts == {
        'normal': 30,
        'ambiguous': 20,
        'missing-information': 15,
        'conflicting-information': 10,
        'hallucination-trap': 10,
        'confidentiality-trap': 5,
    }


def test_gold_set_use_case_distribution():
    counts = Counter(c['use_case'] for c in load_cases())
    assert counts == {'risk': 30, 'status': 30, 'meeting': 30}


def test_every_case_has_reproducible_input_and_gold():
    for case in load_cases():
        assert case['case_id']
        assert case['use_case'] in {'risk', 'status', 'meeting'}
        assert case['category']
        assert case['input_text'].strip()
        assert isinstance(case['gold'], dict)
        assert isinstance(case['grading'], dict)


def test_confidentiality_cases_require_block_and_no_echo():
    for case in load_cases():
        if case['category'] == 'confidentiality-trap':
            assert case['gold'].get('expected_outcome') == 'BLOCK_CONFIDENTIAL_INPUT'
            assert case['grading'].get('block_if_sensitive_token_present') is True
            assert case['grading'].get('must_not_echo_sensitive_values') is True


def test_unknown_is_used_for_unsupported_fields():
    cases = load_cases()
    unknown_cases = [c for c in cases if c['category'] in {'ambiguous', 'missing-information'}]
    assert unknown_cases
    serialized = json.dumps(unknown_cases, ensure_ascii=False)
    assert 'UNKNOWN' in serialized
