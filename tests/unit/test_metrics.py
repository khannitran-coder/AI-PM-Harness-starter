from src.evaluators.metrics import precision_recall_f1, time_saved_pct


def test_f1():
    m = precision_recall_f1({"A", "B"}, {"A", "C"})
    assert round(m.precision, 3) == 0.5
    assert round(m.recall, 3) == 0.5
    assert round(m.f1, 3) == 0.5


def test_time_saved():
    assert round(time_saved_pct(40, 10), 3) == 0.75
