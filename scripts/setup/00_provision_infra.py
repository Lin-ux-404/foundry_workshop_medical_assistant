#!/usr/bin/env python3
"""Provision the resource group, storage, Search, Foundry, telemetry, and model deployments (safe to rerun)."""

from __future__ import annotations

import argparse
import os

from azure.core.exceptions import HttpResponseError, ResourceExistsError
from azure.mgmt.cognitiveservices import CognitiveServicesManagementClient
from azure.mgmt.cognitiveservices.models import (
    Account,
    AccountProperties,
    Deployment,
    DeploymentModel,
    DeploymentProperties,
)
from azure.mgmt.cognitiveservices.models import Identity as CognitiveIdentity
from azure.mgmt.cognitiveservices.models import Project, ProjectProperties
from azure.mgmt.cognitiveservices.models import Sku as CognitiveSku
from azure.mgmt.resource.resources import ResourceManagementClient
from azure.mgmt.storage import StorageManagementClient
from azure.mgmt.storage.models import Kind as StorageKind
from azure.mgmt.storage.models import Sku as StorageSku
from azure.mgmt.storage.models import StorageAccountCreateParameters

from common import Settings, get_credential, load_settings, logger

# The "serverless" search SKU and the `knowledgeRetrieval` surface (Foundry IQ /
# knowledge bases) are preview-only and not yet in the stable azure-mgmt-search
# models, so the search service is created with a raw ARM PUT via the generic
# resource client -- the same approach 05_connect_kb_to_foundry.py uses for the
# (also preview) project connection resource.
SEARCH_API_VERSION = "2026-03-01-Preview"


def ensure_resource_group(resource_client: ResourceManagementClient, settings: Settings) -> None:
    resource_client.resource_groups.create_or_update(
        settings.resource_group, {"location": settings.foundry_location}
    )
    logger.success(f"resource group {settings.resource_group} ({settings.foundry_location})")


def ensure_storage_account(storage_client: StorageManagementClient, settings: Settings) -> None:
    poller = storage_client.storage_accounts.begin_create(
        settings.resource_group,
        settings.storage_account,
        StorageAccountCreateParameters(
            sku=StorageSku(name="Standard_LRS"),
            kind=StorageKind.STORAGE_V2,
            location=settings.data_location,
            access_tier="Hot",
            minimum_tls_version="TLS1_2",
            allow_blob_public_access=False,
            enable_https_traffic_only=True,
            # Some tenants default new storage accounts to publicNetworkAccess
            # "Disabled" (private-endpoint-only); the pipeline talks to blob
            # storage over the public endpoint, so this must be explicit.
            public_network_access="Enabled",
            # This sandbox tenant runs a security policy that force-disables
            # public network access on untagged storage accounts (regardless
            # of what publicNetworkAccess is set to above) unless the account
            # opts out with this tag -- matching the tag already present on
            # the umc-dev workshop's own umcdevstorage account.
            tags={"SecurityControl": "Ignore"},
        ),
    )
    poller.result()
    logger.success(f"storage account {settings.storage_account} ({settings.data_location})")


def ensure_search_service(resource_client: ResourceManagementClient, settings: Settings) -> None:
    body = {
        "location": settings.data_location,
        "identity": {"type": "SystemAssigned"},
        "sku": {"name": settings.search_sku},
        "properties": {
            "hostingMode": "default",
            "publicNetworkAccess": "enabled",
            "disableLocalAuth": True,
            "semanticSearch": settings.semantic_search,
        },
    }
    poller = resource_client.resources.begin_create_or_update_by_id(
        settings.search_service_resource_id, body, api_version=SEARCH_API_VERSION
    )
    poller.result()
    logger.success(
        f"search service {settings.search_service} "
        f"({settings.data_location}, sku={settings.search_sku})"
    )


def ensure_foundry_account(cognitive_client: CognitiveServicesManagementClient, settings: Settings) -> None:
    account = Account(
        location=settings.foundry_location,
        kind="AIServices",
        sku=CognitiveSku(name="S0"),
        identity=CognitiveIdentity(type="SystemAssigned"),
        properties=AccountProperties(
            custom_sub_domain_name=settings.foundry_account,
            public_network_access="Enabled",
            disable_local_auth=True,
            allow_project_management=True,
        ),
    )
    try:
        cognitive_client.accounts.begin_create(
            settings.resource_group, settings.foundry_account, account
        ).result()
    except ResourceExistsError as error:
        if error.error is None or error.error.code != "FlagMustBeSetForRestore":
            raise
        # A previous run created this same account (its name is deterministic
        # per resource group) and it was later deleted; Cognitive Services
        # soft-deletes accounts for a retention window instead of removing
        # them immediately. Since nothing depends on the old one, purge it
        # and create fresh rather than restore it.
        logger.warning(f"purging soft-deleted foundry account {settings.foundry_account}...")
        cognitive_client.deleted_accounts.begin_purge(
            settings.foundry_location, settings.resource_group, settings.foundry_account
        ).result()
        cognitive_client.accounts.begin_create(
            settings.resource_group, settings.foundry_account, account
        ).result()
    logger.success(f"foundry account {settings.foundry_account} ({settings.foundry_location})")


def ensure_foundry_project(cognitive_client: CognitiveServicesManagementClient, settings: Settings) -> None:
    poller = cognitive_client.projects.begin_create(
        settings.resource_group,
        settings.foundry_account,
        settings.foundry_project,
        Project(
            location=settings.foundry_location,
            identity=CognitiveIdentity(type="SystemAssigned"),
            properties=ProjectProperties(display_name=settings.foundry_project),
        ),
    )
    poller.result()
    logger.success(f"foundry project {settings.foundry_project}")


def ensure_telemetry(resource_client: ResourceManagementClient, settings: Settings) -> None:
    resource_group_id = (
        f"/subscriptions/{settings.subscription_id}/resourceGroups/{settings.resource_group}"
    )
    workspace_id = (
        f"{resource_group_id}/providers/Microsoft.OperationalInsights"
        f"/workspaces/{settings.log_analytics_workspace}"
    )
    insights_id = (
        f"{resource_group_id}/providers/Microsoft.Insights/components/{settings.application_insights}"
    )
    resources = resource_client.resources
    resources.begin_create_or_update_by_id(
        workspace_id,
        {
            "location": settings.foundry_location,
            "properties": {
                "sku": {"name": "PerGB2018"},
                "retentionInDays": 30,
                "features": {"enableLogAccessUsingOnlyResourcePermissions": True},
            },
        },
        api_version="2023-09-01",
    ).result()
    resources.begin_create_or_update_by_id(
        insights_id,
        {
            "location": settings.foundry_location,
            "kind": "web",
            "properties": {
                "Application_Type": "web",
                "WorkspaceResourceId": workspace_id,
                # Lab 7's exporter uses a connection string without an Entra credential.
                "DisableLocalAuth": False,
                "publicNetworkAccessForIngestion": "Enabled",
                "publicNetworkAccessForQuery": "Enabled",
            },
        },
        api_version="2020-02-02",
    ).result()
    insights = resources.get_by_id(insights_id, api_version="2020-02-02")
    connection_string = insights.properties.get("ConnectionString")
    if not isinstance(connection_string, str) or not connection_string.strip():
        raise RuntimeError("Application Insights did not return a connection string.")

    # Lab 7's SDK lookup needs a project connection, not just an environment variable.
    resources.begin_create_or_update_by_id(
        f"{settings.project_resource_id}/connections/{settings.app_insights_connection_name}",
        {
            "properties": {
                "category": "AppInsights",
                "authType": "ApiKey",
                "target": insights_id,
                "isSharedToAll": True,
                "credentials": {"key": connection_string},
                "metadata": {"ResourceId": insights_id},
            },
        },
        api_version="2025-10-01-preview",
    ).result()
    logger.success(f"Application Insights {settings.application_insights} connected to Foundry")


def resolve_model_version(
    cognitive_client: CognitiveServicesManagementClient, location: str, model_name: str
) -> str:
    """Look up the current default version of a model in a region.

    Deployments pin a specific model version, and Azure retires old versions
    over time. Reading the version marked ``is_default_version`` from the
    catalogue (instead of hard-coding one here) means this script keeps
    working after Azure ships a new default.
    """
    candidates = [m for m in cognitive_client.models.list(location) if m.model.name == model_name]
    if not candidates:
        raise SystemExit(f"model {model_name!r} is not offered in {location!r}")
    default = next((m for m in candidates if m.model.is_default_version), candidates[0])
    return default.model.version


def ensure_deployment(
    cognitive_client: CognitiveServicesManagementClient,
    settings: Settings,
    name: str,
    model_name: str,
    sku_name: str,
    capacity: int,
) -> None:
    version = resolve_model_version(cognitive_client, settings.foundry_location, model_name)
    try:
        poller = cognitive_client.deployments.begin_create_or_update(
            settings.resource_group,
            settings.foundry_account,
            name,
            Deployment(
                sku=CognitiveSku(name=sku_name, capacity=capacity),
                properties=DeploymentProperties(
                    model=DeploymentModel(format="OpenAI", name=model_name, version=version),
                ),
            ),
        )
        poller.result()
    except HttpResponseError as error:
        if error.error is not None and error.error.code == "InsufficientQuota":
            raise SystemExit(
                f"Not enough '{model_name}' quota in {settings.foundry_location!r} for a "
                f"{capacity}k TPM deployment ({error.error.message}). This quota is shared "
                "across every deployment of that model in the region for this subscription, "
                "so the umc-dev workshop's own deployment eats into what's left for new ones. "
                "Either lower EMBEDDING_CAPACITY/CHAT_CAPACITY to what's available, pick a "
                "different FOUNDRY_LOCATION/DATA_LOCATION with spare quota, or request a quota "
                "increase for this subscription."
            ) from error
        raise
    logger.success(f"deployment {name} ({model_name} {version}, {sku_name} x{capacity})")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "--resource-group",
        default=None,
        help="Override RESOURCE_GROUP for this run (default: env var, then 'umc-dev').",
    )
    parser.add_argument(
        "--subscription-id",
        default=None,
        help="Override SUBSCRIPTION_ID for this run (default: env var, then "
        "`az account show`'s current subscription).",
    )
    args = parser.parse_args()
    if args.resource_group:
        os.environ["RESOURCE_GROUP"] = args.resource_group
    if args.subscription_id:
        os.environ["SUBSCRIPTION_ID"] = args.subscription_id

    settings = load_settings()
    credential = get_credential()

    resource_client = ResourceManagementClient(credential, settings.subscription_id)
    storage_client = StorageManagementClient(credential, settings.subscription_id)
    cognitive_client = CognitiveServicesManagementClient(credential, settings.subscription_id)

    logger.info(f"Using subscription {settings.subscription_id}")
    logger.info(f"Provisioning resource group {settings.resource_group}...")
    ensure_resource_group(resource_client, settings)

    logger.info(f"Provisioning storage account {settings.storage_account}...")
    ensure_storage_account(storage_client, settings)

    logger.info(f"Provisioning search service {settings.search_service}...")
    ensure_search_service(resource_client, settings)

    logger.info(f"Provisioning Foundry account {settings.foundry_account}...")
    ensure_foundry_account(cognitive_client, settings)
    logger.info(f"Provisioning Foundry project {settings.foundry_project}...")
    ensure_foundry_project(cognitive_client, settings)

    logger.info("Provisioning telemetry and connecting it to Foundry...")
    ensure_telemetry(resource_client, settings)

    logger.info("Provisioning model deployments...")
    ensure_deployment(
        cognitive_client,
        settings,
        settings.embedding_deployment,
        settings.embedding_model,
        settings.embedding_sku,
        settings.embedding_capacity,
    )
    ensure_deployment(
        cognitive_client,
        settings,
        settings.chat_deployment,
        settings.chat_model,
        settings.chat_sku,
        settings.chat_capacity,
    )


if __name__ == "__main__":
    main()
