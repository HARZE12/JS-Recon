import subprocess
import tempfile
import os
import json


def run_trufflehog(js_content: str) -> list[dict]:
    """
    Run trufflehog filesystem scan on JS content.
    Returns list of finding dicts. Empty list if trufflehog not installed.
    """
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".js", delete=False, encoding="utf-8"
    ) as f:
        f.write(js_content)
        tmp = f.name

    try:
        result = subprocess.run(
            ["trufflehog", "filesystem", tmp, "--json", "--no-update"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        os.unlink(tmp)

        findings = []
        for line in result.stdout.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                findings.append(json.loads(line))
            except json.JSONDecodeError:
                findings.append({"raw": line})

        return findings

    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        if os.path.exists(tmp):
            os.unlink(tmp)
        return []
