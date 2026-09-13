#!/usr/bin/env bash
# Create the Foundry project connection that lets agents call the knowledge base
# over MCP. Idempotent: a PUT with the same body is a no-op.
#
# The connection uses ProjectManagedIdentity, so no secret is stored anywhere -
# the project's own identity authenticates to Azure AI Search, which is why
# 00_assign_roles.sh grants that identity Search Index Data Reader.
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/config.sh"

MCP_TARGET="${SEARCH_ENDPOINT}/knowledgebases/${KNOWLEDGE_BASE}/mcp?api-version=${SEARCH_API_VERSION}"

body=$(jq -n --arg name "$KB_CONNECTION_NAME" --arg target "$MCP_TARGET" --arg kb "$KNOWLEDGE_BASE" '{
  name: $name,
  type: "Microsoft.MachineLearningServices/workspaces/connections",
  properties: {
    authType: "ProjectManagedIdentity",
    category: "RemoteTool",
    target: $target,
    isSharedToAll: true,
    audience: "https://search.azure.com/",
    metadata: { ApiType: "Azure", type: "knowledgeBase_MCP", knowledgeBaseName: $kb }
  }
}')

token=$(az account get-access-token --scope https://management.azure.com/.default --query accessToken -o tsv)
out=$(curl -s -w '\n%{http_code}' -X PUT \
  -H "Authorization: Bearer ${token}" -H 'Content-Type: application/json' \
  --data-binary "$body" \
  "https://management.azure.com${PROJECT_RESOURCE_ID}/connections/${KB_CONNECTION_NAME}?api-version=2025-10-01-preview")

status=$(tail -n1 <<<"$out")
if [[ "$status" == 2* ]]; then
  echo "  ok  connection ${KB_CONNECTION_NAME} -> ${KNOWLEDGE_BASE} (HTTP ${status})"
else
  echo "  FAIL connection ${KB_CONNECTION_NAME} (HTTP ${status})" >&2
  sed '$d' <<<"$out" >&2
  exit 1
fi
