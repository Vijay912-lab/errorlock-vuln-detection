from errorlock.types import CastleSample, Prediction, ScoredPrediction, normalize_cwe


def _make(true_vuln, pred_vuln, true_cwe=None, pred_cwe=None, parse_error=None):
    sample = CastleSample(sample_id="s1", code="int x;", vulnerable=true_vuln, cwe=true_cwe)
    prediction = Prediction(
        vulnerable=pred_vuln,
        cwe=normalize_cwe(pred_cwe),
        parse_error=parse_error,
    )
    return ScoredPrediction(sample=sample, prediction=prediction, model="test", method="baseline")


def test_binary_correct_true_positive():
    sp = _make(True, True, true_cwe="CWE-120", pred_cwe="CWE-120")
    assert sp.binary_correct


def test_binary_correct_true_negative():
    sp = _make(False, False)
    assert sp.binary_correct


def test_binary_wrong():
    sp = _make(True, False)
    assert not sp.binary_correct
    assert sp.failure_type == "wrong_binary_label"


def test_cwe_correct_when_not_vulnerable():
    sp = _make(False, False)
    assert sp.cwe_correct


def test_cwe_wrong():
    sp = _make(True, True, true_cwe="CWE-120", pred_cwe="CWE-89")
    assert sp.binary_correct
    assert not sp.cwe_correct
    assert sp.failure_type == "wrong_cwe"


def test_parse_error_failure_type():
    sp = _make(True, None, parse_error="no json")
    assert sp.failure_type == "parse_error"
    assert not sp.binary_correct


def test_normalize_cwe_variants():
    assert normalize_cwe("120") == "CWE-120"
    assert normalize_cwe("CWE120") == "CWE-120"
    assert normalize_cwe("cwe-120") == "CWE-120"
    assert normalize_cwe(None) is None
