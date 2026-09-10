#!/usr/bin/env bash
# Idempotently assign the RBAC roles the pipeline needs, scoped to umc-dev only.
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/config.sh"

SEARCH_MI=$(az search service show -g "$RESOURCE_GROUP" -n "$SEARCH_SERVICE" --query identity.principalId -o tsv)
ME=$(az ad signed-in-user show --query id -o tsv)

STORAGE_SCOPE="$STORAGE_RESOURCE_ID"
FOUNDRY_SCOPE="/subscriptions/${SUBSCRIPTION_ID}/resourceGroups/${RESOURCE_GROUP}/providers/Microsoft.CognitiveServices/accounts/${FOUNDRY_ACCOUNT}"
SEARCH_SCOPE="/subscriptions/${SUBSCRIPTION_ID}/resourceGroups/${RESOURCE_GROUP}/providers/Microsoft.Search/searchServices/${SEARCH_SERVICE}"

assign() { # principalId role scope label
  if az role assignment list --assignee "$1" --role "$2" --scope "$3" --query "[0].id" -o tsv | grep -q .; then
    echo "  have  $4"
  else
    az role assignment create --assignee-object-id "$1" --assignee-principal-type "$5" \
      --role "$2" --scope "$3" -o none
    echo "  added $4"
  fi
}

# Search service managed identity -> read blobs, call the embedding/chat deployments.
assign "$SEARCH_MI" "Storage Blob Data Reader"  "$STORAGE_SCOPE" "search MI -> Storage Blob Data Reader"        ServicePrincipal
assign "$SEARCH_MI" "Cognitive Services User"   "$FOUNDRY_SCOPE" "search MI -> Cognitive Services User"          ServicePrincipal

# Operator -> manage search objects, upload blobs, and call /retrieve.
assign "$ME" "Search Service Contributor"     "$SEARCH_SCOPE"  "me -> Search Service Contributor"     User
assign "$ME" "Search Index Data Contributor"  "$SEARCH_SCOPE"  "me -> Search Index Data Contributor"  User
assign "$ME" "Search Index Data Reader"       "$SEARCH_SCOPE"  "me -> Search Index Data Reader"       User
assign "$ME" "Storage Blob Data Contributor"  "$STORAGE_SCOPE" "me -> Storage Blob Data Contributor"  User
