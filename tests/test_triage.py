from steps.triage import triage_js


JS_WITH_IDOR = "fetch('/api/users/' + userId + '/profile')"
JS_WITH_SSRF = "fetch(userInput + '/internal/admin')"
JS_WITH_SECRET = "var aws_key = 'AKIAIOSFODNN7EXAMPLE';"
JS_WITH_XSS = "element.innerHTML = userInput;"
JS_WITH_REDIRECT = "window.location.href = redirectUrl;"
JS_WITH_OAUTH = "https://accounts.google.com/o/oauth2/auth"
JS_WITH_ADMIN = "if (user.role === 'admin') { showAdminPanel(); }"
JS_WITH_UPLOAD = "formData.append('file', fileInput.files[0]);"
JS_WITH_SQLi = "query = 'SELECT * FROM users WHERE id=' + userId"
JS_WITH_RCE = "exec(userInput)"
JS_WITH_LFI = "require('../../../etc/passwd')"
JS_CLEAN = "var x = 1; console.log(x);"


def test_idor_pattern_detected():
    results = triage_js(JS_WITH_IDOR)
    assert "idor" in results
    assert len(results["idor"]) > 0


def test_ssrf_pattern_detected():
    results = triage_js(JS_WITH_SSRF)
    assert "ssrf" in results
    assert len(results["ssrf"]) > 0


def test_secrets_pattern_detected():
    results = triage_js(JS_WITH_SECRET)
    assert "secrets" in results
    assert len(results["secrets"]) > 0


def test_xss_pattern_detected():
    results = triage_js(JS_WITH_XSS)
    assert "xss" in results
    assert len(results["xss"]) > 0


def test_redirect_pattern_detected():
    results = triage_js(JS_WITH_REDIRECT)
    assert "redirect" in results
    assert len(results["redirect"]) > 0


def test_clean_js_returns_empty_buckets():
    results = triage_js(JS_CLEAN)
    total_hits = sum(len(v) for v in results.values())
    assert total_hits == 0


def test_all_expected_categories_present():
    results = triage_js(JS_CLEAN)
    expected = {"idor", "ssrf", "secrets", "xss", "redirect", "oauth", "admin", "upload", "sqli", "rce", "lfi", "webhook", "debug"}
    assert expected.issubset(set(results.keys()))
