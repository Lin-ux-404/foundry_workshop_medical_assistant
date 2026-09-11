#!/usr/bin/env python3
"""Create or update the search pipeline: data source, index, skillset, indexer,
knowledge source, and Foundry IQ knowledge base. Safe to rerun.

    python scripts/medical_kb/03_create_search_pipeline.py [--skip-run] [--reset]

After the objects are created, this triggers an indexer run and waits
(bounded) for it to finish. The preview `azure-search-documents` SDK does not
yet expose an SDK-native "wait for completion" call, so this keeps a small,
documented polling loop instead of a hand-rolled bash `sleep` loop.
"""

from __future__ import annotations

import argparse
import time

from common import HERE, Settings, load_settings, render_template, search_index_client, search_indexer_client

OBJECTS_DIR = HERE / "search_objects"

RUN_POLL_INTERVAL_SECONDS = 15
RUN_POLL_MAX_ATTEMPTS = 80


def create_pipeline(settings: Settings) -> None:
    index_client = search_index_client(settings)
    indexer_client = search_indexer_client(settings)

    print(f"search service {settings.search_service} (api-version {settings.search_api_version})")

    datasource = render_template(OBJECTS_DIR / "datasource.json", settings)
    index = render_template(OBJECTS_DIR / "index.json", settings)
    skillset = render_template(OBJECTS_DIR / "skillset.json", settings)
    indexer = render_template(OBJECTS_DIR / "indexer.json", settings)
    knowledge_source = render_template(OBJECTS_DIR / "knowledge_source.json", settings)
    knowledge_base = render_template(OBJECTS_DIR / "knowledge_base.json", settings)

    indexer_client.create_or_update_data_source_connection(datasource)
    print(f"  ok  datasource {settings.data_source}")
    index_client.create_or_update_index(index)
    print(f"  ok  index {settings.search_index}")
    indexer_client.create_or_update_skillset(skillset)
    print(f"  ok  skillset {settings.skillset}")
    indexer_client.create_or_update_indexer(indexer)
    print(f"  ok  indexer {settings.indexer}")
    index_client.create_or_update_knowledge_source(knowledge_source)
    print(f"  ok  knowledge source {settings.knowledge_source}")
    index_client.create_or_update_knowledge_base(knowledge_base)
    print(f"  ok  knowledge base {settings.knowledge_base}")


def run_and_wait(settings: Settings, reset: bool) -> None:
    indexer_client = search_indexer_client(settings)

    status = indexer_client.get_indexer_status(settings.indexer)
    last = status.last_result
    previous_start = last.start_time if last else None

    if last is not None and last.status == "inProgress":
        print("  indexer already running, waiting for it")
    else:
        if reset:
            indexer_client.reset_indexer(settings.indexer)
        indexer_client.run_indexer(settings.indexer)
        print("  run requested")

    # Wait for a run that finished *after* the one we observed before triggering,
    # otherwise a stale 'success' from the previous run ends the wait immediately.
    final = None
    for _ in range(RUN_POLL_MAX_ATTEMPTS):
        time.sleep(RUN_POLL_INTERVAL_SECONDS)
        status = indexer_client.get_indexer_status(settings.indexer)
        final = status.last_result
        if final is not None and final.status != "inProgress" and final.start_time != previous_start:
            break

    if final is None:
        print("  WARN no indexer run result observed")
        return

    print(
        f"  status={final.status} processed={final.item_count} "
        f"failed={final.failed_item_count} warnings={len(final.warnings or [])}"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--skip-run", action="store_true", help="Only create/update objects, don't trigger ingestion."
    )
    parser.add_argument(
        "--reset", action="store_true", help="Force a full re-ingest (reset the indexer before running)."
    )
    args = parser.parse_args()

    settings = load_settings()
    create_pipeline(settings)
    if not args.skip_run:
        run_and_wait(settings, args.reset)


if __name__ == "__main__":
    main()
