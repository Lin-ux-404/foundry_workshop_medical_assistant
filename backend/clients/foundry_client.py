from azure.identity.aio import DefaultAzureCredential

from agent_framework.foundry import FoundryChatClient

from config import get_settings


def create_credential() -> DefaultAzureCredential:
    return DefaultAzureCredential()


def create_foundry_client(credential: DefaultAzureCredential) -> FoundryChatClient:
    settings = get_settings()
    return FoundryChatClient(
        # Passing None lets the client fall back to AZURE_AI_* env vars.
        project_endpoint=settings.azure_ai_project_endpoint or None,
        model=settings.azure_ai_model_deployment_name or None,
        credential=credential,
    )
