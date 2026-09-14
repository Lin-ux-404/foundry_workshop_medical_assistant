#!/usr/bin/env python3
"""Create the blob container and upload the WHO PDFs with citation metadata.

    python scripts/setup/03_upload_blobs.py

Uses Microsoft Entra auth only (``DefaultAzureCredential``); no account keys
are read or printed.
"""

from __future__ import annotations

import sys

from azure.core.exceptions import ResourceExistsError
from azure.storage.blob import BlobServiceClient, ContentSettings

from common import documents_manifest, get_credential, load_settings

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

    print(f"container {settings.blob_container} in {settings.storage_account}")
    try:
        container.create_container()
    except ResourceExistsError:
        pass

    for doc in documents:
        file_name = doc["file"]
        path = settings.docs_dir / file_name
        if not path.exists() or path.stat().st_size == 0:
            sys.exit(f"  FAIL missing {path} - run 02_download_docs.py")

        metadata = {field: str(doc[field]) for field in METADATA_FIELDS}
        with path.open("rb") as fh:
            container.upload_blob(
                name=file_name,
                data=fh,
                overwrite=True,
                metadata=metadata,
                content_settings=ContentSettings(content_type="application/pdf"),
            )
        print(f"  ok    {file_name}")


if __name__ == "__main__":
    main()
