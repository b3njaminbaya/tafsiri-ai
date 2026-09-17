from training.promote_language import MIN_BLEU, MIN_CHRF, check_report


def test_check_report_passes_when_above_floor():
    report = {"bleu": MIN_BLEU + 5, "chrf": MIN_CHRF + 5, "test_examples": 50}
    passed, reasons = check_report(report)
    assert passed is True
    assert reasons == []


def test_check_report_fails_low_bleu():
    report = {"bleu": MIN_BLEU - 1, "chrf": MIN_CHRF + 5, "test_examples": 50}
    passed, reasons = check_report(report)
    assert passed is False
    assert any("BLEU" in r for r in reasons)


def test_check_report_fails_low_chrf():
    report = {"bleu": MIN_BLEU + 5, "chrf": MIN_CHRF - 1, "test_examples": 50}
    passed, reasons = check_report(report)
    assert passed is False
    assert any("chrF" in r for r in reasons)


def test_check_report_fails_too_few_test_examples_even_with_good_scores():
    report = {"bleu": MIN_BLEU + 50, "chrf": MIN_CHRF + 50, "test_examples": 3}
    passed, reasons = check_report(report)
    assert passed is False
    assert any("test examples" in r for r in reasons)


def test_check_report_reports_all_failing_reasons_at_once():
    report = {"bleu": 0.0, "chrf": 0.0, "test_examples": 1}
    passed, reasons = check_report(report)
    assert passed is False
    assert len(reasons) == 3
