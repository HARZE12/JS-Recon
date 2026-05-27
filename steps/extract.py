import json
from pathlib import Path

JS_MIME_TYPES = {
    "application/javascript",
    "text/javascript",
    "application/x-javascript",
}


def extract_js_from_har(har_path: str) -> list[dict]:
    """Return list of {url, content} dicts for all JS entries in the HAR."""
    path = Path(har_path)
    if not path.exists():
        raise FileNotFoundError(f"HAR file not found: {har_path}")

    with open(path, encoding="utf-8", errors="replace") as f:
        data = json.load(f)

    results = []
    for entry in data.get("log", {}).get("entries", []):
        mime = entry.get("response", {}).get("content", {}).get("mimeType", "")
        mime_base = mime.split(";")[0].strip().lower()
        if mime_base not in JS_MIME_TYPES:
            continue
        content = entry.get("response", {}).get("content", {}).get("text", "")
        url = entry.get("request", {}).get("url", "unknown")
        if content:
            results.append({"url": url, "content": content})

    return results
