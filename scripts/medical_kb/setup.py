#!/usr/bin/env python3
"""End-to-end, rerunnable setup for the WHO medical knowledge base.

    az login
    python scripts/medical_kb/setup.py --resource-group my-rg
    python scripts/medical_kb/setup.py --resource-group my-rg --reset-indexer

Every step is idempotent, and all auth is Microsoft Entra - no secrets are
read, written, or printed.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def run(script: str, *extra_args: str) -> None:
    subprocess.run([sys.executable, str(HERE / script), *extra_args], check=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "--resource-group",
        default=os.environ.get("RESOURCE_GROUP", "umc-dev"),
        help="Resource group to deploy into (default: %(default)s).",
    )
    parser.add_argument(
        "--reset-indexer", action="store_true", help="Force a full re-ingest of all documents."
    )
    args = parser.parse_args()

    # Every step reads its config from common.py, which reads this env var -
    # setting it once here means none of the numbered scripts need to know
    # about --resource-group.
    os.environ["RESOURCE_GROUP"] = args.resource_group

    print("\n=== 0/5 role assignments")
    run("00_assign_roles.py")

    print("\n=== 1/5 download WHO PDFs")
    run("01_download_docs.py")

    print("\n=== 2/5 upload to blob storage")
    run("02_upload_blobs.py")

    print("\n=== 3/5 create search pipeline + run ingestion")
    run("03_create_search_pipeline.py", *(["--reset"] if args.reset_indexer else []))

    print("\n=== 4/5 connect the knowledge base to Foundry")
    run("05_connect_kb_to_foundry.py")

    print("\n=== 5/5 verify")
    run("04_verify.py")


if __name__ == "__main__":
    main()
