#!/usr/bin/env python3
"""Create the blob container and upload the WHO PDFs with citation metadata."""

from __future__ import annotations

import sys

from azure.core.exceptions import ResourceExistsError
from azure.storage.blob import BlobServiceClient, ContentSettings

from common import documents_manifest, get_credential, load_settings, logger, retry_on_transient_error

METADATA_FIELDS = [
    "document_title",
    "source_url",
    "publisher",
    "publication_id",
    "topic",
    "license",
    "license_url",
    "citation",
]


def main() -> None:
    settings = load_settings()
    documents = documents_manifest()

    account_url = f"https://{settings.storage_account}.blob.core.windows.net"
    service = BlobServiceClient(account_url, credential=get_credential())
    container = service.get_container_client(settings.blob_container)

    logger.info(f"container {settings.blob_container} in {settings.storage_account}")

    def _create_container() -> None:
        try:
            container.create_container()
        except ResourceExistsError:
            pass  # already exists -- not a transient error, don't retry

    # 01_assign_roles.py may have just granted this identity's Storage Blob
    # Data Contributor role moments ago; that grant can take a while to
    # propagate through Microsoft Entra, so a fresh role can 403 here.
    retry_on_transient_error(_create_container)

    for doc in documents:
        file_name = doc["file"]
        path = settings.docs_dir / file_name
        if not path.exists() or path.stat().st_size == 0:
            sys.exit(f"missing {path} - run 02_download_docs.py")

        metadata = {field: str(doc[field]) for field in METADATA_FIELDS}

        def _upload_blob() -> None:
            with path.open("rb") as fh:
                container.upload_blob(
                    name=file_name,
                    data=fh,
                    overwrite=True,
                    metadata=metadata,
                    content_settings=ContentSettings(content_type="application/pdf"),
                )

        # Reopen the file on every attempt so a retry re-reads from the start
        # instead of resuming a stream that a failed request already advanced.
        retry_on_transient_error(_upload_blob)
        logger.success(file_name)


if __name__ == "__main__":
    main()
