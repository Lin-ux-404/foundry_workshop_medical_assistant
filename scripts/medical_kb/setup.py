#!/usr/bin/env python3
"""End-to-end, rerunnable setup for the WHO medical knowledge base.

    az login
    python scripts/medical_kb/setup.py --resource-group my-rg
    python scripts/medical_kb/setup.py --resource-group my-rg --reset-indexer
    python scripts/medical_kb/setup.py --resource-group my-rg --skip-provision

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

    steps = 6 if args.skip_provision else 7
    step = 0

    if not args.skip_provision:
        step += 1
        print(f"\n=== {step}/{steps} provision infrastructure")
        run("00_provision_infra.py")

    step += 1
    print(f"\n=== {step}/{steps} role assignments")
    run("01_assign_roles.py")

    step += 1
    print(f"\n=== {step}/{steps} download WHO PDFs")
    run("02_download_docs.py")

    step += 1
    print(f"\n=== {step}/{steps} upload to blob storage")
    run("03_upload_blobs.py")

    step += 1
    print(f"\n=== {step}/{steps} create search pipeline + run ingestion")
    run("04_create_search_pipeline.py", *(["--reset"] if args.reset_indexer else []))

    step += 1
    print(f"\n=== {step}/{steps} connect the knowledge base to Foundry")
    run("05_connect_kb_to_foundry.py")

    step += 1
    print(f"\n=== {step}/{steps} verify")
    run("06_verify.py")


if __name__ == "__main__":
    main()
