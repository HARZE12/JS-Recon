from patterns import PATTERNS


def triage_js(content: str) -> dict[str, list[str]]:
    """
    Run all triage patterns against JS content.
    Returns dict of category -> list of matching lines.
    """
    results: dict[str, list[str]] = {category: [] for category in PATTERNS}

    lines = content.splitlines()
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        for category, compiled_patterns in PATTERNS.items():
            for pattern in compiled_patterns:
                if pattern.search(stripped):
                    results[category].append(stripped)
                    break  # one match per category per line

    return results
