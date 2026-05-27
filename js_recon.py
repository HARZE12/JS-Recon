#!/usr/bin/env python3
"""JS Recon Kit v2 — HAR-based JavaScript reconnaissance automation."""

import argparse
import json
import os
import sys
from pathlib import Path
from urllib.parse import urlparse

from steps.extract import extract_js_from_har
from steps.beautify import beautify_js
from steps.triage import triage_js
from steps.linkfinder import run_linkfinder
from steps.secretfinder import run_secretfinder
from steps.trufflehog import run_trufflehog
from steps.keycheck import extract_keys, validate_keys
from steps.summary import build_summary


def slugify_url(url: str) -> str:
    """Convert URL to a safe directory name."""
    parsed = urlparse(url)
    host = parsed.netloc or url
    return host.replace(".", "_").replace(":", "_")


def safe_filename(url: str, index: int) -> str:
    """Derive a short filename from a JS URL."""
    path = urlparse(url).path
    name = Path(path).stem or f"script_{index}"
    return f"{name}_{index}.js"


def write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", errors="replace")


def run(args: argparse.Namespace) -> None:
    print(f"[*] Loading HAR: {args.har}")

    js_entries = extract_js_from_har(args.har)
    if not js_entries:
        print("[!] No JavaScript entries found in HAR. Exiting.")
        sys.exit(0)

    print(f"[+] Found {len(js_entries)} JS entries")

    first_url = js_entries[0]["url"]
    slug = slugify_url(first_url)
    out_dir = Path(args.output or f"recon_{slug}")
    print(f"[*] Output directory: {out_dir}")

    all_endpoints: list[str] = []
    all_triage: dict[str, list[str]] = {}
    all_key_results: list[dict] = []
    secrets_count = 0

    for i, entry in enumerate(js_entries):
        url = entry["url"]
        content = entry["content"]
        fname = safe_filename(url, i)
        print(f"  [{i+1}/{len(js_entries)}] {url}")

        beautified = beautify_js(content)
        write_file(out_dir / "js" / fname, beautified)

        if not args.skip_lf:
            endpoints = run_linkfinder(beautified, args.linkfinder)
            if endpoints:
                write_file(out_dir / "endpoints" / f"{fname}.txt", "\n".join(endpoints))
                all_endpoints.extend(endpoints)

        if not args.skip_sf:
            secrets = run_secretfinder(beautified, args.secretfinder)
            if secrets:
                write_file(out_dir / "secrets" / f"sf_{fname}.txt", "\n".join(secrets))
                secrets_count += len(secrets)

        if not args.skip_th:
            th_findings = run_trufflehog(beautified)
            if th_findings:
                write_file(
                    out_dir / "secrets" / f"th_{fname}.json",
                    json.dumps(th_findings, indent=2),
                )
                secrets_count += len(th_findings)

        if not args.skip_triage:
            file_triage = triage_js(beautified)
            for category, hits in file_triage.items():
                if hits:
                    all_triage.setdefault(category, []).extend(hits)

        if not args.skip_keys:
            found_keys = extract_keys(beautified)
            if found_keys:
                all_key_results.extend(validate_keys(found_keys))

    for category, hits in all_triage.items():
        unique_hits = list(dict.fromkeys(hits))
        write_file(out_dir / "triage" / f"{category}.txt", "\n".join(unique_hits))

    if all_key_results:
        write_file(
            out_dir / "keys" / "results.json",
            json.dumps(all_key_results, indent=2),
        )

    summary = build_summary(
        target=first_url,
        js_count=len(js_entries),
        triage_results=all_triage,
        endpoints=list(dict.fromkeys(all_endpoints)),
        secrets_count=secrets_count,
        key_results=all_key_results,
    )
    write_file(out_dir / "summary.txt", summary)
    print("\n" + summary, flush=True)
    print(f"\n[+] Done. Results saved to: {out_dir}/")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="JS Recon Kit v2 — HAR-based JavaScript recon automation"
    )
    parser.add_argument("har", help="Path to the .har file")
    parser.add_argument("--output", "-o", help="Output directory (default: recon_<target>)")
    parser.add_argument("--linkfinder", default="linkfinder.py", help="Path to linkfinder.py")
    parser.add_argument("--secretfinder", default="SecretFinder.py", help="Path to SecretFinder.py")
    parser.add_argument("--skip-lf", action="store_true", help="Skip LinkFinder")
    parser.add_argument("--skip-sf", action="store_true", help="Skip SecretFinder")
    parser.add_argument("--skip-th", action="store_true", help="Skip trufflehog")
    parser.add_argument("--skip-triage", action="store_true", help="Skip triage patterns")
    parser.add_argument("--skip-keys", action="store_true", help="Skip API key validation")
    args = parser.parse_args()

    if not os.path.exists(args.har):
        print(f"[!] HAR file not found: {args.har}")
        sys.exit(1)

    run(args)


if __name__ == "__main__":
    main()
