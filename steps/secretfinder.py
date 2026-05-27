import subprocess
import tempfile
import os


def run_secretfinder(js_content: str, secretfinder_path: str = "SecretFinder.py") -> list[str]:
    """
    Run SecretFinder on JS content. Returns list of found secrets.
    Returns empty list if SecretFinder is not installed.
    """
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".js", delete=False, encoding="utf-8"
    ) as f:
        f.write(js_content)
        tmp = f.name

    try:
        result = subprocess.run(
            ["python3", secretfinder_path, "-i", tmp, "-o", "cli"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        os.unlink(tmp)

        if result.returncode != 0:
            return []

        return [line.strip() for line in result.stdout.splitlines() if line.strip()]

    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        if os.path.exists(tmp):
            os.unlink(tmp)
        return []
