#!/usr/bin/env python3
"""Download the three WHO guideline PDFs. Safe to rerun: existing valid PDFs are kept.

    python scripts/medical_kb/01_download_docs.py
"""

from __future__ import annotations

import sys

import requests

from common import documents_manifest, load_settings

RETRY_ATTEMPTS = 3
# iris.who.int returns 403 for the default python-requests user agent.
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; medical-kb-setup/1.0)"}


def is_pdf(path) -> bool:
    return path.exists() and path.stat().st_size > 0 and path.read_bytes()[:4] == b"%PDF"


def download(url: str, target) -> None:
    last_error: Exception | None = None
    for attempt in range(1, RETRY_ATTEMPTS + 1):
        try:
            response = requests.get(url, headers=HEADERS, timeout=60)
            response.raise_for_status()
            target.write_bytes(response.content)
            return
        except requests.RequestException as exc:  # network hiccup, blip, etc.
            last_error = exc
            print(f"  retry {attempt}/{RETRY_ATTEMPTS} for {url}: {exc}")
    raise SystemExit(f"  FAIL  could not download {url}: {last_error}")


def main() -> None:
    settings = load_settings()
    settings.docs_dir.mkdir(parents=True, exist_ok=True)

    for doc in documents_manifest():
        file_name = doc["file"]
        target = settings.docs_dir / file_name

        if is_pdf(target):
            print(f"  skip  {file_name} (already downloaded, {target.stat().st_size} bytes)")
            continue

        print(f"  get   {file_name}")
        download(doc["pdf_url"], target)
        if not is_pdf(target):
            sys.exit(f"  FAIL  {file_name} is not a PDF")
        print(f"  ok    {file_name} ({target.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
