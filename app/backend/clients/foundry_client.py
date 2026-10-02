from azure.identity.aio import AzureCliCredential, ClientSecretCredential

from agent_framework.foundry import FoundryChatClient

from config import get_settings


def create_credential() -> AzureCliCredential | ClientSecretCredential:
    settings = get_settings()
    if settings.has_service_principal:
        return ClientSecretCredential(
            tenant_id=settings.azure_tenant_id,
            client_id=settings.azure_client_id,
            client_secret=settings.azure_client_secret.get_secret_value(),
        )
    # Use the developer's signed-in CLI identity when no service principal is
    # configured, so unrelated credentials cannot shadow the intended login.
    return AzureCliCredential()


def create_foundry_client(credential: AzureCliCredential | ClientSecretCredential) -> FoundryChatClient:
    settings = get_settings()
    return FoundryChatClient(
        # Passing None lets the client fall back to AZURE_AI_* env vars.
        project_endpoint=settings.azure_ai_project_endpoint or None,
        model=settings.azure_ai_model_deployment_name or None,
        credential=credential,
    )
