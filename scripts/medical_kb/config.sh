#!/usr/bin/env bash
# Shared, non-secret configuration for the WHO medical knowledge base.
# No keys or connection secrets live here: everything authenticates with Microsoft Entra.

# --- Azure scope (never widen beyond this resource group) ---
export SUBSCRIPTION_ID="${SUBSCRIPTION_ID:-df5e62d1-9c33-4157-8fae-26629b63a4a5}"
export RESOURCE_GROUP="${RESOURCE_GROUP:-umc-dev}"

# --- Existing resources that are reused, never re-created ---
export STORAGE_ACCOUNT="${STORAGE_ACCOUNT:-umcdevstorage}"
export SEARCH_SERVICE="${SEARCH_SERVICE:-umc-hackathon-devbox-fiq-search}"
export SEARCH_ENDPOINT="${SEARCH_ENDPOINT:-https://${SEARCH_SERVICE}.search.windows.net}"
export FOUNDRY_ACCOUNT="${FOUNDRY_ACCOUNT:-umc-hackathon-devbox-resource}"
export FOUNDRY_ENDPOINT="${FOUNDRY_ENDPOINT:-https://${FOUNDRY_ACCOUNT}.cognitiveservices.azure.com}"
export FOUNDRY_PROJECT="${FOUNDRY_PROJECT:-umc-hackathon-devbox}"

# --- Model deployments (must already exist in the Foundry account) ---
export EMBEDDING_DEPLOYMENT="${EMBEDDING_DEPLOYMENT:-text-embedding-3-large}"
export EMBEDDING_MODEL="${EMBEDDING_MODEL:-text-embedding-3-large}"
export EMBEDDING_DIMENSIONS="${EMBEDDING_DIMENSIONS:-3072}"
export CHAT_DEPLOYMENT="${CHAT_DEPLOYMENT:-gpt-5.6-luna}"
export CHAT_MODEL="${CHAT_MODEL:-gpt-5.6-luna}"

# --- Objects created by this project ---
export BLOB_CONTAINER="${BLOB_CONTAINER:-who-guidelines}"
export DATA_SOURCE="${DATA_SOURCE:-who-guidelines-datasource}"
export SEARCH_INDEX="${SEARCH_INDEX:-who-guidelines-index}"
export SKILLSET="${SKILLSET:-who-guidelines-skillset}"
export INDEXER="${INDEXER:-who-guidelines-indexer}"
export SEMANTIC_CONFIG="${SEMANTIC_CONFIG:-who-guidelines-semantic}"
export KNOWLEDGE_SOURCE="${KNOWLEDGE_SOURCE:-who-guidelines-ks}"
export KNOWLEDGE_BASE="${KNOWLEDGE_BASE:-umc-medical-kb}"

# --- Foundry project connection that lets agents call the knowledge base over MCP ---
export KB_CONNECTION_NAME="${KB_CONNECTION_NAME:-who-kb-mcp}"
export PROJECT_RESOURCE_ID="/subscriptions/${SUBSCRIPTION_ID}/resourceGroups/${RESOURCE_GROUP}/providers/Microsoft.CognitiveServices/accounts/${FOUNDRY_ACCOUNT}/projects/${FOUNDRY_PROJECT}"
export PROJECT_ENDPOINT="${PROJECT_ENDPOINT:-${FOUNDRY_ENDPOINT}/api/projects/${FOUNDRY_PROJECT}}"

# --- API version: only 2026-08-01-preview is accepted by this serverless service ---
export SEARCH_API_VERSION="${SEARCH_API_VERSION:-2026-08-01-preview}"

# --- Local paths ---
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
export REPO_ROOT
export DOCS_DIR="${DOCS_DIR:-$REPO_ROOT/labs/data/who_guidelines}"

export STORAGE_RESOURCE_ID="/subscriptions/${SUBSCRIPTION_ID}/resourceGroups/${RESOURCE_GROUP}/providers/Microsoft.Storage/storageAccounts/${STORAGE_ACCOUNT}"

# Acquire a data-plane token for Azure AI Search (local auth is disabled on this service).
search_token() {
  az account get-access-token --scope https://search.azure.com/.default --query accessToken -o tsv
}

# search_call METHOD PATH [BODY_FILE] -> prints "HTTP_STATUS<newline>BODY"
search_call() {
  local method="$1" path="$2" body="${3:-}"
  local token; token="$(search_token)"
  local args=(-s -w '\n%{http_code}' -X "$method"
    -H "Authorization: Bearer ${token}" -H 'Content-Type: application/json')
  if [[ -n "$body" ]]; then args+=(--data-binary "@${body}"); else args+=(-H 'Content-Length: 0'); fi
  curl "${args[@]}" "${SEARCH_ENDPOINT}${path}?api-version=${SEARCH_API_VERSION}"
}

# put_object PATH RENDERED_JSON_FILE LABEL -- idempotent create-or-update
put_object() {
  local path="$1" file="$2" label="$3"
  local out status
  out="$(search_call PUT "$path" "$file")"
  status="$(tail -n1 <<<"$out")"
  if [[ "$status" == 2* ]]; then
    echo "  ok  ${label} (HTTP ${status})"
  else
    echo "  FAIL ${label} (HTTP ${status})" >&2
    sed '$d' <<<"$out" >&2
    return 1
  fi
}

# Render a JSON template, substituting only the ${VARS} we own.
render() {
  envsubst '$SUBSCRIPTION_ID $RESOURCE_GROUP $STORAGE_ACCOUNT $STORAGE_RESOURCE_ID $BLOB_CONTAINER
            $DATA_SOURCE $SEARCH_INDEX $SKILLSET $INDEXER $SEMANTIC_CONFIG
            $KNOWLEDGE_SOURCE $KNOWLEDGE_BASE
            $FOUNDRY_ENDPOINT $EMBEDDING_DEPLOYMENT $EMBEDDING_MODEL $EMBEDDING_DIMENSIONS
            $CHAT_DEPLOYMENT $CHAT_MODEL' < "$1"
}
