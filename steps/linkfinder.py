import subprocess
import tempfile
import os


def run_linkfinder(js_content: str, linkfinder_path: str = "linkfinder.py") -> list[str]:
    """
    Run LinkFinder on JS content. Returns list of discovered endpoints.
    Returns empty list if LinkFinder is not installed.
    """
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".js", delete=False, encoding="utf-8"
    ) as f:
        f.write(js_content)
        tmp = f.name

    try:
        result = subprocess.run(
            ["python3", linkfinder_path, "-i", tmp, "-o", "cli"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        os.unlink(tmp)

        if result.returncode != 0:
            return []

        endpoints = [
            line.strip()
            for line in result.stdout.splitlines()
            if line.strip() and not line.startswith("[")
        ]
        return endpoints

    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        if os.path.exists(tmp):
            os.unlink(tmp)
        return []
