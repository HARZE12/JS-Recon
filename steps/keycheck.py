import re
import urllib.request
import urllib.error
import json as _json

KEY_PATTERNS: dict[str, re.Pattern] = {
    "aws": re.compile(r"AKIA[0-9A-Z]{16}"),
    "google": re.compile(r"AIza[0-9A-Za-z\-_]{35}"),
    "stripe_live": re.compile(r"sk_live_[0-9a-zA-Z]{24,}"),
    "stripe_test": re.compile(r"sk_test_[0-9a-zA-Z]{24,}"),
    "twilio": re.compile(r"SK[0-9a-fA-F]{32}"),
    "sendgrid": re.compile(r"SG\.[0-9A-Za-z\-_]{22}\.[0-9A-Za-z\-_]{43}"),
    "heroku": re.compile(r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}"),
    "github": re.compile(r"gh[pousr]_[0-9A-Za-z]{36}"),
    "slack": re.compile(r"xox[baprs]-[0-9A-Za-z\-]{10,}"),
}


def _check_google(key: str) -> bool:
    try:
        url = f"https://www.googleapis.com/oauth2/v1/tokeninfo?access_token={key}"
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=5) as resp:
            return resp.status == 200
    except Exception:
        return False


def _check_stripe(key: str) -> bool:
    try:
        import base64
        creds = base64.b64encode(f"{key}:".encode()).decode()
        req = urllib.request.Request(
            "https://api.stripe.com/v1/charges",
            headers={"Authorization": f"Basic {creds}"},
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            return resp.status != 401
    except urllib.error.HTTPError as e:
        return e.code != 401
    except Exception:
        return False


def _check_slack(key: str) -> bool:
    try:
        data = b""
        req = urllib.request.Request(
            "https://slack.com/api/auth.test",
            data=data,
            headers={"Authorization": f"Bearer {key}"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            body = _json.loads(resp.read())
            return bool(body.get("ok", False))
    except Exception:
        return False


# Validators must be defined before this dict
VALIDATORS: dict[str, object] = {
    "google": _check_google,
    "stripe_live": _check_stripe,
    "slack": _check_slack,
}


def extract_keys(content: str) -> dict[str, list[str]]:
    """Extract all recognizable API keys from JS content."""
    found: dict[str, list[str]] = {}
    for key_type, pattern in KEY_PATTERNS.items():
        matches = pattern.findall(content)
        if matches:
            found[key_type] = list(set(matches))
    return found


def validate_keys(found_keys: dict[str, list[str]]) -> list[dict]:
    """
    Validate each found key against its service.
    Returns list of {type, key, valid, note} dicts.
    """
    results = []
    for key_type, keys in found_keys.items():
        validator = VALIDATORS.get(key_type)
        for key in keys:
            valid = validator(key) if validator else None
            results.append({
                "type": key_type,
                "key": key,
                "valid": valid,
                "note": "no validator" if validator is None else ("VALID ⚠️" if valid else "invalid"),
            })
    return results
