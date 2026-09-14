#!/usr/bin/env python3
"""Create the Foundry project connection that lets agents call the knowledge base over MCP (idempotent)."""

from __future__ import annotations

from azure.mgmt.resource.resources import ResourceManagementClient

from common import Settings, get_credential, load_settings, logger

CONNECTION_API_VERSION = "2025-10-01-preview"


def main() -> None:
    settings: Settings = load_settings()
    resource_client = ResourceManagementClient(get_credential(), settings.subscription_id)

    connection_id = f"{settings.project_resource_id}/connections/{settings.kb_connection_name}"
    body = {
        "name": settings.kb_connection_name,
        "type": "Microsoft.MachineLearningServices/workspaces/connections",
        "properties": {
            "authType": "ProjectManagedIdentity",
            "category": "RemoteTool",
            "target": settings.mcp_target,
            "isSharedToAll": True,
            "audience": "https://search.azure.com/",
            "metadata": {
                "ApiType": "Azure",
                "type": "knowledgeBase_MCP",
                "knowledgeBaseName": settings.knowledge_base,
            },
        },
    }

    poller = resource_client.resources.begin_create_or_update_by_id(
        connection_id, body, api_version=CONNECTION_API_VERSION
    )
    poller.result()
    logger.success(f"connection {settings.kb_connection_name} -> {settings.knowledge_base}")


if __name__ == "__main__":
    main()
