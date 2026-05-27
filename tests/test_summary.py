from steps.summary import build_summary


def test_summary_contains_target():
    result = build_summary(
        target="https://example.com",
        js_count=3,
        triage_results={"idor": ["line1", "line2"], "xss": [], "ssrf": ["line3"]},
        endpoints=["/api/users", "/api/admin"],
        secrets_count=1,
        key_results=[{"type": "aws", "key": "AKIAIOSFODNN7EXAMPLE", "valid": True, "note": "VALID ⚠️"}],
    )
    assert "example.com" in result


def test_summary_shows_js_count():
    result = build_summary(
        target="https://example.com",
        js_count=5,
        triage_results={},
        endpoints=[],
        secrets_count=0,
        key_results=[],
    )
    assert "5" in result


def test_summary_highlights_valid_keys():
    result = build_summary(
        target="https://x.com",
        js_count=1,
        triage_results={},
        endpoints=[],
        secrets_count=0,
        key_results=[{"type": "stripe_live", "key": "sk_live_abc", "valid": True, "note": "VALID ⚠️"}],
    )
    assert "VALID" in result


def test_summary_shows_triage_counts():
    result = build_summary(
        target="https://x.com",
        js_count=1,
        triage_results={"idor": ["a", "b", "c"], "xss": ["d"]},
        endpoints=[],
        secrets_count=0,
        key_results=[],
    )
    assert "idor" in result.lower()
    assert "3" in result
