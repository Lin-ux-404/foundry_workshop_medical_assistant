#!/usr/bin/env python3
"""Create or update the search pipeline: data source, index, skillset, indexer, knowledge source, and Foundry IQ knowledge base (safe to rerun)."""

from __future__ import annotations

import argparse
import time

from azure.core.exceptions import ResourceNotFoundError

from common import HERE, Settings, load_settings, logger, render_template, retry_on_transient_error, search_index_client, search_indexer_client

OBJECTS_DIR = HERE / "search_objects"

RUN_POLL_INTERVAL_SECONDS = 15
RUN_POLL_MAX_ATTEMPTS = 80


def create_pipeline(settings: Settings) -> None:
    index_client = search_index_client(settings)
    indexer_client = search_indexer_client(settings)

    logger.info(f"search service {settings.search_service} (api-version {settings.search_api_version})")

    datasource = render_template(OBJECTS_DIR / "datasource.json", settings)
    index = render_template(OBJECTS_DIR / "index.json", settings)
    skillset = render_template(OBJECTS_DIR / "skillset.json", settings)
    indexer = render_template(OBJECTS_DIR / "indexer.json", settings)
    knowledge_source = render_template(OBJECTS_DIR / "knowledge_source.json", settings)
    knowledge_base = render_template(OBJECTS_DIR / "knowledge_base.json", settings)

    indexer_client.create_or_update_data_source_connection(datasource)
    logger.success(f"datasource {settings.data_source}")
    # The index's vectorizer and the skillset's embedding skill both call out
    # to the Foundry account, so both can transiently fail here if
    # 01_assign_roles.py's Cognitive Services User grant hasn't propagated yet.
    retry_on_transient_error(lambda: index_client.create_or_update_index(index))
    logger.success(f"index {settings.search_index}")
    retry_on_transient_error(lambda: indexer_client.create_or_update_skillset(skillset))
    logger.success(f"skillset {settings.skillset}")
    indexer_client.create_or_update_indexer(indexer)
    logger.success(f"indexer {settings.indexer}")
    index_client.create_or_update_knowledge_source(knowledge_source)
    logger.success(f"knowledge source {settings.knowledge_source}")
    index_client.create_or_update_knowledge_base(knowledge_base)
    logger.success(f"knowledge base {settings.knowledge_base}")


def run_and_wait(settings: Settings, previous_start, reset: bool) -> None:
    indexer_client = search_indexer_client(settings)

    if reset:
        # create_or_update_indexer() may have already auto-triggered its own
        # run; let that settle first so reset_indexer() doesn't fight over
        # indexer state with a run still in progress.
        for _ in range(RUN_POLL_MAX_ATTEMPTS):
            if indexer_client.get_indexer_status(settings.indexer).status != "running":
                break
            time.sleep(RUN_POLL_INTERVAL_SECONDS)
        # A plain indexer run only reprocesses blobs that changed since the
        # last run; --reset-indexer needs a genuine full reprocess, so clear
        # the incremental change-tracking state and trigger a fresh run.
        indexer_client.reset_indexer(settings.indexer)
        indexer_client.run_indexer(settings.indexer)
        logger.info("full re-ingest requested")
    else:
        # create_or_update_indexer() in create_pipeline() already
        # auto-triggers a run for any new or changed indexer definition, so
        # there's nothing to trigger here -- calling run_indexer() again
        # would just queue a redundant second run right behind it.
        logger.info("waiting for the run the indexer update already triggered")

    # Wait for a run that finished *after* the one we observed before
    # create_pipeline() touched the indexer, otherwise a stale 'success' from
    # an earlier run ends the wait immediately.
    final = None
    for _ in range(RUN_POLL_MAX_ATTEMPTS):
        time.sleep(RUN_POLL_INTERVAL_SECONDS)
        status = indexer_client.get_indexer_status(settings.indexer)
        final = status.last_result
        if final is not None and final.status != "inProgress" and final.start_time != previous_start:
            break

    if final is None:
        logger.warning("no indexer run result observed")
        return

    logger.success(
        f"status={final.status.value} processed={final.item_count} "
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

    # Capture the run pointer *before* create_pipeline() touches the indexer:
    # creating or updating an indexer auto-triggers a run, so this baseline
    # is what lets run_and_wait() recognize *that* run finishing instead of
    # an older one still sitting in last_result.
    previous_start = None
    if not args.skip_run:
        try:
            status = search_indexer_client(settings).get_indexer_status(settings.indexer)
            previous_start = status.last_result.start_time if status.last_result else None
        except ResourceNotFoundError:
            pass  # indexer doesn't exist yet -- nothing to establish a baseline from

    create_pipeline(settings)
    if not args.skip_run:
        run_and_wait(settings, previous_start, args.reset)


if __name__ == "__main__":
    main()
