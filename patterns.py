import re

PATTERNS: dict[str, list[re.Pattern]] = {
    "idor": [
        re.compile(r"/api/\w+/\$?\{?\w*[Ii][Dd]\w*\}?", re.IGNORECASE),
        re.compile(r"['\"/]\w+/\w*[Ii][Dd]\w*/", re.IGNORECASE),
        re.compile(r"userId|accountId|user_id|account_id|object_id", re.IGNORECASE),
    ],
    "ssrf": [
        re.compile(r"fetch\s*\(\s*\w+", re.IGNORECASE),
        re.compile(r"XMLHttpRequest|axios\.get\s*\(\s*\w+", re.IGNORECASE),
        re.compile(r"url\s*=\s*\w+\s*\+", re.IGNORECASE),
        re.compile(r"http://169\.254\.169\.254", re.IGNORECASE),
        re.compile(r"internal|localhost|127\.0\.0\.1|0\.0\.0\.0", re.IGNORECASE),
    ],
    "secrets": [
        re.compile(r"AKIA[0-9A-Z]{16}", re.IGNORECASE),
        re.compile(r"(api[_-]?key|apikey|secret|token|password|passwd|pwd)\s*[:=]\s*['\"][^'\"]{8,}", re.IGNORECASE),
        re.compile(r"Authorization\s*:\s*['\"]?(Bearer|Basic)\s+\S+", re.IGNORECASE),
        re.compile(r"-----BEGIN (RSA |EC )?PRIVATE KEY-----"),
        re.compile(r"(stripe|twilio|sendgrid|mailgun|heroku)[\w_-]*\s*[:=]\s*['\"][^'\"]{10,}", re.IGNORECASE),
    ],
    "xss": [
        re.compile(r"innerHTML\s*=", re.IGNORECASE),
        re.compile(r"outerHTML\s*=", re.IGNORECASE),
        re.compile(r"document\.write\s*\(", re.IGNORECASE),
        re.compile(r"eval\s*\(", re.IGNORECASE),
        re.compile(r"dangerouslySetInnerHTML", re.IGNORECASE),
    ],
    "redirect": [
        re.compile(r"window\.location\s*=", re.IGNORECASE),
        re.compile(r"window\.location\.href\s*=", re.IGNORECASE),
        re.compile(r"location\.replace\s*\(", re.IGNORECASE),
        re.compile(r"redirect_uri|returnUrl|next=|return_to", re.IGNORECASE),
    ],
    "oauth": [
        re.compile(r"oauth", re.IGNORECASE),
        re.compile(r"client_id|client_secret", re.IGNORECASE),
        re.compile(r"access_token|refresh_token|id_token", re.IGNORECASE),
        re.compile(r"accounts\.google\.com|login\.microsoftonline\.com|github\.com/login/oauth", re.IGNORECASE),
    ],
    "admin": [
        re.compile(r"['\"/]admin['\"/]", re.IGNORECASE),
        re.compile(r"isAdmin|is_admin|role\s*===?\s*['\"]admin", re.IGNORECASE),
        re.compile(r"superuser|privileged|elevated", re.IGNORECASE),
    ],
    "upload": [
        re.compile(r"FormData|multipart/form-data", re.IGNORECASE),
        re.compile(r"fileInput|file_upload|\.files\[", re.IGNORECASE),
        re.compile(r"<input[^>]+type=['\"]file", re.IGNORECASE),
    ],
    "sqli": [
        re.compile(r"SELECT\s+\*?\s+FROM", re.IGNORECASE),
        re.compile(r"(query|sql)\s*[+=]+\s*['\"]?\s*(SELECT|INSERT|UPDATE|DELETE|DROP)", re.IGNORECASE),
        re.compile(r"WHERE\s+\w+\s*=\s*['\"]?\s*\+", re.IGNORECASE),
    ],
    "rce": [
        re.compile(r"\bexec\s*\(", re.IGNORECASE),
        re.compile(r"\beval\s*\(", re.IGNORECASE),
        re.compile(r"child_process|spawn\s*\(|execSync\s*\(", re.IGNORECASE),
        re.compile(r"__import__\s*\(|subprocess\.", re.IGNORECASE),
    ],
    "lfi": [
        re.compile(r"\.\./\.\./", re.IGNORECASE),
        re.compile(r"require\s*\(\s*['\"]?\.\.", re.IGNORECASE),
        re.compile(r"include\s*\(\s*\$", re.IGNORECASE),
        re.compile(r"/etc/passwd|/etc/shadow|/proc/self", re.IGNORECASE),
    ],
    "webhook": [
        re.compile(r"webhook", re.IGNORECASE),
        re.compile(r"hooks\.slack\.com|discord\.com/api/webhooks", re.IGNORECASE),
    ],
    "debug": [
        re.compile(r"console\.(log|debug|warn|error)\s*\(.*?(token|key|secret|password|auth)", re.IGNORECASE),
        re.compile(r"debugger\s*;", re.IGNORECASE),
        re.compile(r"//\s*TODO|//\s*FIXME|//\s*HACK", re.IGNORECASE),
    ],
}
