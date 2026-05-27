from steps.beautify import beautify_js


def test_beautify_expands_minified_code():
    minified = "function foo(){var x=1;var y=2;return x+y;}"
    result = beautify_js(minified)
    assert "\n" in result


def test_beautify_returns_string():
    result = beautify_js("var x = 1;")
    assert isinstance(result, str)


def test_beautify_handles_empty_string():
    result = beautify_js("")
    assert result == ""


def test_beautify_preserves_content():
    code = "var secret = 'abc123';"
    result = beautify_js(code)
    assert "secret" in result
    assert "abc123" in result
