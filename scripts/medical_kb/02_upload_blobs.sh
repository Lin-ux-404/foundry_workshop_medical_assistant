#!/usr/bin/env bash
# Create the blob container and upload the WHO PDFs with citation metadata.
# Uses Microsoft Entra auth only (--auth-mode login); no account keys are read or printed.
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/config.sh"

manifest="$(dirname "${BASH_SOURCE[0]}")/documents.json"

echo "container ${BLOB_CONTAINER} in ${STORAGE_ACCOUNT}"
az storage container create \
  --account-name "$STORAGE_ACCOUNT" \
  --name "$BLOB_CONTAINER" \
  --auth-mode login \
  --only-show-errors -o none

jq -c '.[]' "$manifest" | while read -r doc; do
  file=$(jq -r '.file' <<<"$doc")
  [[ -s "$DOCS_DIR/$file" ]] || { echo "  FAIL missing $DOCS_DIR/$file - run 01_download_docs.sh" >&2; exit 1; }
  az storage blob upload \
    --account-name "$STORAGE_ACCOUNT" \
    --container-name "$BLOB_CONTAINER" \
    --auth-mode login \
    --file "$DOCS_DIR/$file" \
    --name "$file" \
    --overwrite \
    --content-type application/pdf \
    --metadata \
      document_title="$(jq -r '.document_title' <<<"$doc")" \
      source_url="$(jq -r '.source_url' <<<"$doc")" \
      publisher="$(jq -r '.publisher' <<<"$doc")" \
      publication_id="$(jq -r '.publication_id' <<<"$doc")" \
      topic="$(jq -r '.topic' <<<"$doc")" \
      license="$(jq -r '.license' <<<"$doc")" \
      license_url="$(jq -r '.license_url' <<<"$doc")" \
      citation="$(jq -r '.citation' <<<"$doc")" \
    --no-progress --only-show-errors -o none
  echo "  ok    $file"
done
