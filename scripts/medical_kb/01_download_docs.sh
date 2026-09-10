#!/usr/bin/env bash
# Download the three WHO guideline PDFs. Safe to rerun: existing valid PDFs are kept.
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/config.sh"

mkdir -p "$DOCS_DIR"
manifest="$(dirname "${BASH_SOURCE[0]}")/documents.json"

jq -r '.[] | [.file, .pdf_url] | @tsv' "$manifest" | while IFS=$'\t' read -r file url; do
  target="$DOCS_DIR/$file"
  if [[ -s "$target" ]] && head -c 5 "$target" | grep -q '%PDF'; then
    echo "  skip  $file (already downloaded, $(stat -c%s "$target") bytes)"
    continue
  fi
  echo "  get   $file"
  curl -fsSL --retry 3 -o "$target" "$url"
  head -c 5 "$target" | grep -q '%PDF' || { echo "  FAIL  $file is not a PDF" >&2; exit 1; }
  echo "  ok    $file ($(stat -c%s "$target") bytes)"
done
