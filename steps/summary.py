from datetime import datetime


def build_summary(
    target: str,
    js_count: int,
    triage_results: dict[str, list[str]],
    endpoints: list[str],
    secrets_count: int,
    key_results: list[dict],
) -> str:
    """Build a text summary report of the recon run."""
    lines = [
        "=" * 60,
        "JS RECON KIT v2 — SUMMARY",
        "=" * 60,
        f"Target:      {target}",
        f"Date:        {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"JS files:    {js_count}",
        f"Endpoints:   {len(endpoints)}",
        f"Secrets:     {secrets_count}",
        "",
        "TRIAGE RESULTS",
        "-" * 40,
    ]

    for category, hits in triage_results.items():
        if hits:
            lines.append(f"  {category:<12} {len(hits)} hit(s)")

    total_hits = sum(len(v) for v in triage_results.values())
    lines += ["", f"Total triage hits: {total_hits}", ""]

    if key_results:
        lines += ["API KEYS FOUND", "-" * 40]
        for k in key_results:
            lines.append(f"  [{k['type']}] {k['key'][:20]}...  -> {k['note']}")
        lines.append("")

    valid_keys = [k for k in key_results if k.get("valid")]
    if valid_keys:
        lines += [
            "⚠️  VALID KEYS DETECTED — REPORT IMMEDIATELY",
            "-" * 40,
        ]
        for k in valid_keys:
            lines.append(f"  {k['type']}: {k['key']}")
        lines.append("")

    lines += ["=" * 60, "Review buckets in: recon_<target>/triage/", "=" * 60]
    return "\n".join(lines)
