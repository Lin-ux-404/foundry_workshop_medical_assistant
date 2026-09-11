#!/usr/bin/env python3
"""End-to-end, rerunnable setup for the WHO medical knowledge base in umc-dev.

    az login
    python scripts/medical_kb/setup.py
    python scripts/medical_kb/setup.py --reset-indexer   # force a full re-ingest

Every step is idempotent. Nothing outside the umc-dev resource group is touched,
and no secrets are read, written, or printed - all auth is Microsoft Entra.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def run(script: str, extra_args: list[str] | None = None) -> None:
    subprocess.run(
        [sys.executable, str(HERE / script), *(extra_args or [])],
        check=True,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--reset-indexer", action="store_true", help="Force a full re-ingest of all documents."
    )
    args = parser.parse_args()

    print("\n=== 0/5 role assignments")
    run("00_assign_roles.py")

    print("\n=== 1/5 download WHO PDFs")
    run("01_download_docs.py")

    print("\n=== 2/5 upload to blob storage")
    run("02_upload_blobs.py")

    print("\n=== 3/5 create search pipeline + run ingestion")
    run("03_create_search_pipeline.py", ["--reset"] if args.reset_indexer else None)

    print("\n=== 4/5 connect the knowledge base to Foundry")
    run("05_connect_kb_to_foundry.py")

    print("\n=== 5/5 verify")
    run("04_verify.py")


if __name__ == "__main__":
    main()
