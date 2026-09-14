#!/usr/bin/env python3
"""Idempotently assign the RBAC roles the pipeline needs.

    python scripts/setup/01_assign_roles.py

Uses the same Microsoft Entra session as the rest of the pipeline
(``DefaultAzureCredential``): run ``az login`` first. Every assignment is
checked before it is created, so this is safe to rerun.
"""

from __future__ import annotations

from uuid import uuid4

import requests
from azure.mgmt.authorization import AuthorizationManagementClient
from azure.mgmt.resource.resources import ResourceManagementClient
from azure.mgmt.search import SearchManagementClient

from common import Settings, get_credential, load_settings

# Stable, tenant-independent GUIDs for Azure built-in roles (identical in
# every subscription -- these are not secrets).
ROLE_DEFINITION_IDS = {
    "Storage Blob Data Reader": "2a2b9908-6ea1-4ae2-8e65-a410df84e7d1",
    "Storage Blob Data Contributor": "ba92f5b4-2d11-453d-a403-e96b0029c9fe",
    "Cognitive Services User": "a97b65f3-24c7-4388-baec-2e87135dc908",
    "Search Index Data Reader": "1407120a-92aa-4202-b7e9-c0e197c71c8f",
    "Search Index Data Contributor": "8ebe5a00-799e-43f5-93ac-243d3dce84a7",
    "Search Service Contributor": "7ca78c08-252a-4471-8644-bb5ff32d4ba0",
}

# The Foundry "project" sub-resource is only exposed at this preview API
# version; there is no stable management SDK for it yet, so we read it with
# the generic ARM resource client instead.
PROJECT_API_VERSION = "2025-06-01"


def signed_in_user_id() -> str:
    """The operator's own Entra object id (equivalent to `az ad signed-in-user show`)."""
    token = get_credential().get_token("https://graph.microsoft.com/.default").token
    response = requests.get(
        "https://graph.microsoft.com/v1.0/me",
        headers={"Authorization": "Bearer " + token},
        params={"$select": "id"},
        timeout=30,
    )
    response.raise_for_status()
    return response.json()["id"]


def assign(
    auth_client: AuthorizationManagementClient,
    subscription_id: str,
    principal_id: str,
    principal_type: str,
    role: str,
    scope: str,
    label: str,
) -> None:
    role_definition_id = (
        f"/subscriptions/{subscription_id}/providers/Microsoft.Authorization"
        f"/roleDefinitions/{ROLE_DEFINITION_IDS[role]}"
    )
    existing = auth_client.role_assignments.list_for_scope(
        scope, filter=f"principalId eq '{principal_id}'"
    )
    if any(a.role_definition_id.lower() == role_definition_id.lower() for a in existing):
        print(f"  have  {label}")
        return

    auth_client.role_assignments.create(
        scope,
        role_assignment_name=str(uuid4()),
        parameters={
            "properties": {
                "roleDefinitionId": role_definition_id,
                "principalId": principal_id,
                "principalType": principal_type,
            }
        },
    )
    print(f"  added {label}")


def main() -> None:
    settings: Settings = load_settings()
    credential = get_credential()

    search_mgmt = SearchManagementClient(credential, settings.subscription_id)
    search_mi = search_mgmt.services.get(
        settings.resource_group, settings.search_service
    ).identity.principal_id

    resource_mgmt = ResourceManagementClient(credential, settings.subscription_id)
    project_mi = resource_mgmt.resources.get_by_id(
        settings.project_resource_id, api_version=PROJECT_API_VERSION
    ).identity.principal_id

    me = signed_in_user_id()

    storage_scope = settings.storage_resource_id
    foundry_scope = settings.foundry_account_resource_id
    search_scope = settings.search_service_resource_id

    # (principal, principal type, role, scope, log label)
    assignments = [
        # Search service managed identity -> read blobs, call the embedding/chat deployments.
        (search_mi, "ServicePrincipal", "Storage Blob Data Reader", storage_scope, "search MI -> Storage Blob Data Reader"),
        (search_mi, "ServicePrincipal", "Cognitive Services User", foundry_scope, "search MI -> Cognitive Services User"),
        # Foundry project managed identity -> call the knowledge base's /retrieve over MCP.
        (project_mi, "ServicePrincipal", "Search Index Data Reader", search_scope, "project MI -> Search Index Data Reader"),
        # Operator -> manage search objects, upload blobs, and call /retrieve.
        (me, "User", "Search Service Contributor", search_scope, "me -> Search Service Contributor"),
        (me, "User", "Search Index Data Contributor", search_scope, "me -> Search Index Data Contributor"),
        (me, "User", "Search Index Data Reader", search_scope, "me -> Search Index Data Reader"),
        (me, "User", "Storage Blob Data Contributor", storage_scope, "me -> Storage Blob Data Contributor"),
    ]

    auth_client = AuthorizationManagementClient(credential, settings.subscription_id)
    for principal_id, principal_type, role, scope, label in assignments:
        assign(auth_client, settings.subscription_id, principal_id, principal_type, role, scope, label)


if __name__ == "__main__":
    main()
