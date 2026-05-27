import subprocess
import tempfile
import os
import jsbeautifier


def beautify_js(content: str) -> str:
    """Beautify JS using jsbeautifier, with prettier as optional fallback."""
    if not content.strip():
        return ""

    opts = jsbeautifier.default_options()
    opts.indent_size = 2
    opts.wrap_line_length = 120
    result = jsbeautifier.beautify(content, opts)

    prettier_result = _try_prettier(content)
    if prettier_result:
        return prettier_result

    return result


def _try_prettier(content: str) -> str | None:
    """Attempt to beautify with prettier. Returns None if not available."""
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".js", delete=False, encoding="utf-8"
        ) as f:
            f.write(content)
            tmp = f.name

        result = subprocess.run(
            ["prettier", "--parser", "babel", tmp],
            capture_output=True,
            text=True,
            timeout=10,
        )
        os.unlink(tmp)

        if result.returncode == 0 and result.stdout.strip():
            return result.stdout
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        pass
    return None
