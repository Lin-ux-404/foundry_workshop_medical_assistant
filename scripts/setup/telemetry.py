#!/usr/bin/env python3
"""Provision Lab 7 telemetry, or add it to an existing workshop project (safe to rerun)."""

from __future__ import annotations

from azure.mgmt.resource.resources import ResourceManagementClient

from common import Settings, get_credential, load_settings, logger

WORKSPACE_API_VERSION = "2023-09-01"
INSIGHTS_API_VERSION = "2020-02-02"
CONNECTION_API_VERSION = "2025-10-01-preview"


def ensure_telemetry(resource_client: ResourceManagementClient, settings: Settings) -> None:
    resources = resource_client.resources
    resources.begin_create_or_update_by_id(
        settings.log_analytics_resource_id,
        {
            "location": settings.telemetry_location,
            "properties": {
                "sku": {"name": "PerGB2018"},
                "retentionInDays": 30,
                "features": {"enableLogAccessUsingOnlyResourcePermissions": True},
            },
        },
        api_version=WORKSPACE_API_VERSION,
    ).result()
    logger.success(f"Log Analytics workspace {settings.log_analytics_workspace}")

    resources.begin_create_or_update_by_id(
        settings.application_insights_resource_id,
        {
            "location": settings.telemetry_location,
            "kind": "web",
            "properties": {
                "Application_Type": "web",
                "WorkspaceResourceId": settings.log_analytics_resource_id,
                # Lab 7's exporter uses a connection string without an Entra credential.
                "DisableLocalAuth": False,
                "publicNetworkAccessForIngestion": "Enabled",
                "publicNetworkAccessForQuery": "Enabled",
            },
        },
        api_version=INSIGHTS_API_VERSION,
    ).result()
    logger.success(f"Application Insights {settings.application_insights}")

    insights = resources.get_by_id(
        settings.application_insights_resource_id, api_version=INSIGHTS_API_VERSION
    )
    connection_string = insights.properties.get("ConnectionString")
    if not isinstance(connection_string, str) or not connection_string.strip():
        raise RuntimeError("Application Insights did not return a connection string.")

    # The SDK telemetry lookup reads this project's AppInsights connection,
    # not an APPLICATIONINSIGHTS_CONNECTION_STRING environment variable.
    resources.begin_create_or_update_by_id(
        settings.app_insights_connection_resource_id,
        {
            "properties": {
                "category": "AppInsights",
                "authType": "ApiKey",
                "target": settings.application_insights_resource_id,
                "isSharedToAll": True,
                "credentials": {"key": connection_string},
                "metadata": {"ResourceId": settings.application_insights_resource_id},
            },
        },
        api_version=CONNECTION_API_VERSION,
    ).result()
    logger.success(f"Foundry telemetry connection {settings.app_insights_connection_name}")


def verify_telemetry(resource_client: ResourceManagementClient, settings: Settings) -> None:
    resources = resource_client.resources
    resources.get_by_id(settings.log_analytics_resource_id, api_version=WORKSPACE_API_VERSION)
    insights = resources.get_by_id(
        settings.application_insights_resource_id, api_version=INSIGHTS_API_VERSION
    )
    workspace_id = insights.properties.get("WorkspaceResourceId", "")
    if workspace_id.lower() != settings.log_analytics_resource_id.lower():
        raise RuntimeError("Application Insights is not linked to the configured Log Analytics workspace.")
    if insights.properties.get("DisableLocalAuth") is True:
        raise RuntimeError("Application Insights local authentication is disabled; Lab 7 requires it.")

    connection = resources.get_by_id(
        settings.app_insights_connection_resource_id, api_version=CONNECTION_API_VERSION
    )
    properties = connection.properties
    if properties.get("category") != "AppInsights" or properties.get("authType") != "ApiKey":
        raise RuntimeError("The Foundry telemetry connection must use AppInsights with ApiKey authentication.")
    if properties.get("target", "").lower() != settings.application_insights_resource_id.lower():
        raise RuntimeError("The Foundry telemetry connection targets a different Application Insights resource.")
    logger.success("Telemetry workspace, Application Insights and Foundry connection are linked.")


def main() -> None:
    settings = load_settings()
    with ResourceManagementClient(get_credential(), settings.subscription_id) as resource_client:
        ensure_telemetry(resource_client, settings)
        verify_telemetry(resource_client, settings)


if __name__ == "__main__":
    main()
