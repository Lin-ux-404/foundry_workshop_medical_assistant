#!/usr/bin/env python3
"""End-to-end, rerunnable setup for the workshop's Azure environment and
WHO medical knowledge base.

    az login
    python scripts/setup/run.py --resource-group my-rg
    python scripts/setup/run.py --resource-group my-rg --reset-indexer
    python scripts/setup/run.py --resource-group my-rg --skip-provision

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
    parser.add_argument(
        "--skip-provision",
        action="store_true",
        help="Skip 00_provision_infra.py, e.g. when the storage account, search "
        "service, and Foundry project already exist.",
    )
    args = parser.parse_args()

    # Every step reads its config from common.py, which reads this env var -
    # setting it once here means none of the numbered scripts need to know
    # about --resource-group.
    os.environ["RESOURCE_GROUP"] = args.resource_group

    # (script, label, extra args). Skipping provisioning just drops the first entry.
    steps = [
        ("00_provision_infra.py", "provision infrastructure", []),
        ("01_assign_roles.py", "role assignments", []),
        ("02_download_docs.py", "download WHO PDFs", []),
        ("03_upload_blobs.py", "upload to blob storage", []),
        (
            "04_create_search_pipeline.py",
            "create search pipeline + run ingestion",
            ["--reset"] if args.reset_indexer else [],
        ),
        ("05_connect_kb_to_foundry.py", "connect the knowledge base to Foundry", []),
        ("06_verify.py", "verify", []),
    ]
    if args.skip_provision:
        steps = steps[1:]

    for i, (script, label, extra_args) in enumerate(steps, start=1):
        print(f"\n=== {i}/{len(steps)} {label}")
        run(script, *extra_args)


if __name__ == "__main__":
    main()
