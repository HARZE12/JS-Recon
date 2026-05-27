import json
import os
import pytest
from steps.extract import extract_js_from_har


FIXTURE = os.path.join(os.path.dirname(__file__), "fixtures", "sample.har")


def test_extracts_only_js_entries():
    results = extract_js_from_har(FIXTURE)
    assert len(results) == 1


def test_extracted_entry_has_url_and_content():
    results = extract_js_from_har(FIXTURE)
    entry = results[0]
    assert entry["url"] == "https://example.com/static/app.js"
    assert "apiKey" in entry["content"]


def test_returns_empty_list_for_no_js():
    har = {"log": {"entries": [{"request": {"url": "https://x.com"}, "response": {"content": {"mimeType": "text/html", "text": ""}}}]}}
    import tempfile
    with tempfile.NamedTemporaryFile(mode="w", suffix=".har", delete=False) as f:
        json.dump(har, f)
        tmp = f.name
    assert extract_js_from_har(tmp) == []


def test_raises_on_missing_file():
    with pytest.raises(FileNotFoundError):
        extract_js_from_har("nonexistent.har")
