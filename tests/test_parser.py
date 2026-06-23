from errorlock.parser import parse_prediction


def test_parse_plain_json():
    pred = parse_prediction('{"vulnerable": true, "cwe": "120", "location": "line 4"}')
    assert pred.parsed
    assert pred.vulnerable is True
    assert pred.cwe == "CWE-120"


def test_parse_markdown_json():
    pred = parse_prediction('```json\n{"vulnerable": false, "cwe": null}\n```')
    assert pred.parsed
    assert pred.vulnerable is False


def test_parse_failure_is_recorded():
    pred = parse_prediction("not json")
    assert not pred.parsed
    assert pred.parse_error
