#!/usr/bin/env python3
"""Provision the Azure infrastructure the rest of the pipeline runs on: the
resource group, the storage account, the Azure AI Search service, the Foundry
(Cognitive Services `AIServices`) account and project, and the two model
deployments (embeddings + chat) the knowledge base needs. Safe to rerun --
every step is a create-or-update.

    az login
    export SUBSCRIPTION_ID=<your-subscription-id>
    python scripts/setup/00_provision_infra.py --resource-group my-rg

Every object name, region and SKU defaults to the umc-dev workshop setup and
can be overridden via environment variable -- see `common.py`. Authentication
is Microsoft Entra only (`DefaultAzureCredential`); the identity running this
needs Owner or Contributor on the target subscription (or at least on the
resource group, if it already exists).

This step is what turns an empty subscription into something `01_assign_roles.py`
onward can build on -- it does not replace lab 1's "deploy a model in the
portal" exercise, it just means the *rest* of the workshop (labs 2-7 and this
pipeline) has a working project to point at from the start.
"""

from __future__ import annotations

import argparse
import os

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
    poller = cognitive_client.accounts.begin_create(
        settings.resource_group,
        settings.foundry_account,
        Account(
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
        ),
    )
    poller.result()
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
    logger.success(f"deployment {name} ({model_name} {version}, {sku_name} x{capacity})")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "--resource-group",
        default=None,
        help="Override RESOURCE_GROUP for this run (default: env var, then 'umc-dev').",
    )
    args = parser.parse_args()
    if args.resource_group:
        os.environ["RESOURCE_GROUP"] = args.resource_group

    settings = load_settings()
    credential = get_credential()

    resource_client = ResourceManagementClient(credential, settings.subscription_id)
    storage_client = StorageManagementClient(credential, settings.subscription_id)
    cognitive_client = CognitiveServicesManagementClient(credential, settings.subscription_id)

    logger.info(f"subscription {settings.subscription_id}")
    ensure_resource_group(resource_client, settings)

    logger.info("storage account")
    ensure_storage_account(storage_client, settings)

    logger.info("search service")
    ensure_search_service(resource_client, settings)

    logger.info("foundry account + project")
    ensure_foundry_account(cognitive_client, settings)
    ensure_foundry_project(cognitive_client, settings)

    logger.info("model deployments")
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
