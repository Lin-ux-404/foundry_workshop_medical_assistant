#!/usr/bin/env bash
# End-to-end, rerunnable setup for the WHO medical knowledge base in umc-dev.
#
#   az login
#   ./scripts/medical_kb/setup.sh
#
# Every step is idempotent. Nothing outside the umc-dev resource group is touched,
# and no secrets are read, written, or printed - all auth is Microsoft Entra.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$HERE/config.sh"

az account set --subscription "$SUBSCRIPTION_ID"

step() { printf '\n=== %s\n' "$1"; }

step "0/5 role assignments"        ; "$HERE/00_assign_roles.sh"
step "1/5 download WHO PDFs"       ; "$HERE/01_download_docs.sh"
step "2/5 upload to blob storage"  ; "$HERE/02_upload_blobs.sh"
step "3/5 create search pipeline"  ; "$HERE/03_create_search_pipeline.sh"

step "4/5 run ingestion"
status_of() { search_call GET "/indexers/${INDEXER}/status" | sed '$d'; }

s="$(status_of)"
prev_start="$(jq -r '.lastResult.startTime // ""' <<<"$s")"

if [[ "$(jq -r '.lastResult.status // "none"' <<<"$s")" == "inProgress" ]]; then
  echo "  indexer already running, waiting for it"
  prev_start=""   # the in-flight run is the one we wait on
else
  [[ "${RESET_INDEXER:-0}" == "1" ]] && search_call POST "/indexers/${INDEXER}/reset" >/dev/null
  search_call POST "/indexers/${INDEXER}/run" >/dev/null
  echo "  run requested"
fi

# Wait for a run that finished *after* the one we observed before triggering,
# otherwise a stale 'success' from the previous run ends the wait immediately.
for _ in $(seq 1 80); do
  sleep 15
  s="$(status_of)"
  st="$(jq -r '.lastResult.status' <<<"$s")"
  start="$(jq -r '.lastResult.startTime // ""' <<<"$s")"
  [[ "$st" != "inProgress" && "$start" != "$prev_start" ]] && break
done
jq -r '"  status=\(.lastResult.status) processed=\(.lastResult.itemsProcessed) failed=\(.lastResult.itemsFailed) warnings=\(.lastResult.warnings|length)"' <<<"$s"

step "5/5 verify"
PY="${PYTHON:-$REPO_ROOT/.venv/bin/python}"
[[ -x "$PY" ]] || PY=python3
SEARCH_SERVICE="$SEARCH_SERVICE" SEARCH_API_VERSION="$SEARCH_API_VERSION" \
SEARCH_INDEX="$SEARCH_INDEX" INDEXER="$INDEXER" \
KNOWLEDGE_BASE="$KNOWLEDGE_BASE" KNOWLEDGE_SOURCE="$KNOWLEDGE_SOURCE" \
  "$PY" "$HERE/04_verify.py"
