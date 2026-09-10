#!/usr/bin/env bash
# Create or update the search pipeline: data source, index, skillset, indexer,
# knowledge source, and Foundry IQ knowledge base. Safe to rerun.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$HERE/config.sh"

OBJ="$HERE/search_objects"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

echo "search service ${SEARCH_SERVICE} (api-version ${SEARCH_API_VERSION})"

render "$OBJ/datasource.json"       > "$TMP/datasource.json"
render "$OBJ/index.json"            > "$TMP/index.json"
render "$OBJ/skillset.json"         > "$TMP/skillset.json"
render "$OBJ/indexer.json"          > "$TMP/indexer.json"
render "$OBJ/knowledge_source.json" > "$TMP/knowledge_source.json"
render "$OBJ/knowledge_base.json"   > "$TMP/knowledge_base.json"

put_object "/datasources/${DATA_SOURCE}"           "$TMP/datasource.json"       "datasource ${DATA_SOURCE}"
put_object "/indexes/${SEARCH_INDEX}"              "$TMP/index.json"            "index ${SEARCH_INDEX}"
put_object "/skillsets/${SKILLSET}"                "$TMP/skillset.json"         "skillset ${SKILLSET}"
put_object "/indexers/${INDEXER}"                  "$TMP/indexer.json"          "indexer ${INDEXER}"
put_object "/knowledgesources/${KNOWLEDGE_SOURCE}" "$TMP/knowledge_source.json" "knowledge source ${KNOWLEDGE_SOURCE}"
put_object "/knowledgebases/${KNOWLEDGE_BASE}"     "$TMP/knowledge_base.json"   "knowledge base ${KNOWLEDGE_BASE}"
