"""Shared configuration and Azure SDK client factories for the workshop's
environment provisioning and WHO medical knowledge base pipeline.

Every script in this folder imports this module so there is exactly one place
that defines names, endpoints, and authentication. No keys or connection
secrets live here: everything authenticates with Microsoft Entra
(``DefaultAzureCredential``), which picks up your ``az login`` session for
local runs.
"""

from __future__ import annotations

import json
import re
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from azure.identity import DefaultAzureCredential
from loguru import logger

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent.parent

# Windows consoles often default to a legacy codepage (e.g. cp1252) that can't
# encode characters PDFs and model answers commonly contain (>=, en dashes,
# etc). Force UTF-8 on the stream loguru writes to so a log line never
# crashes a report.
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# One logger configuration for every script in this folder: colorized,
# timestamped (date + time), and leveled (INFO/SUCCESS/WARNING/ERROR) instead
# of bare prints, so a long provisioning run is easy to scan or grep.
logger.remove()
logger.add(
    sys.stderr,
    colorize=True,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
)


def _az_cli_subscription_id() -> str | None:
    """The subscription `az login`/`az account set` last selected, i.e. what
    `az account show` reports. Falling back to this means most people never
    need to set SUBSCRIPTION_ID by hand - it's only needed when the Azure CLI
    isn't installed, or you want to target a different subscription than the
    CLI's current default.
    """
    az_cmd = shutil.which("az")
    if not az_cmd:
        return None
    try:
        result = subprocess.run(
            [az_cmd, "account", "show", "--query", "id", "-o", "tsv"],
            capture_output=True,
            text=True,
            timeout=15,
            check=True,
        )
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, OSError):
        return None
    subscription_id = result.stdout.strip()
    return subscription_id or None


def _subscription_id() -> str:
    value = os.environ.get("SUBSCRIPTION_ID") or _az_cli_subscription_id()
    if not value:
        raise SystemExit(
            "Could not determine SUBSCRIPTION_ID. Either run `az login` (so "
            "`az account show` has a subscription to report) or set it "
            "explicitly, e.g.\n"
            '  $env:SUBSCRIPTION_ID = "<value>"   # PowerShell\n'
            "  export SUBSCRIPTION_ID=<value>     # bash"
        )
    return value


@dataclass(frozen=True)
class Settings:
    """Non-secret configuration for the workshop's Azure environment and
    WHO medical knowledge base pipeline."""

    subscription_id: str
    resource_group: str

    storage_account: str
    search_service: str
    search_endpoint: str
    foundry_account: str
    foundry_endpoint: str
    foundry_project: str

    # Provisioning-only settings (00_provision_infra.py). Everything below is
    # unused once the resources already exist, so these are safe to ignore for
    # the rest of the pipeline.
    data_location: str
    foundry_location: str
    search_sku: str
    semantic_search: str

    embedding_deployment: str
    embedding_model: str
    embedding_dimensions: int
    embedding_sku: str
    embedding_capacity: int
    chat_deployment: str
    chat_model: str
    chat_sku: str
    chat_capacity: int

    blob_container: str
    data_source: str
    search_index: str
    skillset: str
    indexer: str
    semantic_config: str
    knowledge_source: str
    knowledge_base: str
    kb_connection_name: str

    search_api_version: str
    docs_dir: Path

    @property
    def storage_resource_id(self) -> str:
        return (
            f"/subscriptions/{self.subscription_id}/resourceGroups/{self.resource_group}"
            f"/providers/Microsoft.Storage/storageAccounts/{self.storage_account}"
        )

    @property
    def search_service_resource_id(self) -> str:
        return (
            f"/subscriptions/{self.subscription_id}/resourceGroups/{self.resource_group}"
            f"/providers/Microsoft.Search/searchServices/{self.search_service}"
        )

    @property
    def foundry_account_resource_id(self) -> str:
        return (
            f"/subscriptions/{self.subscription_id}/resourceGroups/{self.resource_group}"
            f"/providers/Microsoft.CognitiveServices/accounts/{self.foundry_account}"
        )

    @property
    def project_resource_id(self) -> str:
        return f"{self.foundry_account_resource_id}/projects/{self.foundry_project}"

    @property
    def mcp_target(self) -> str:
        return (
            f"{self.search_endpoint}/knowledgebases/{self.knowledge_base}/mcp"
            f"?api-version={self.search_api_version}"
        )


def load_settings() -> Settings:
    """Read pipeline configuration from the environment.

    ``SUBSCRIPTION_ID`` defaults to whatever ``az account show`` reports (the
    subscription ``az login``/``az account set`` last selected), so it only
    needs to be set explicitly (env var) to target a different subscription
    or when the Azure CLI isn't installed. Every other value falls back to
    the umc-dev workshop defaults and can be overridden the same way.
    """
    subscription_id = _subscription_id()
    resource_group = os.environ.get("RESOURCE_GROUP", "umc-dev")

    storage_account = os.environ.get("STORAGE_ACCOUNT", "umcdevstorage")
    search_service = os.environ.get("SEARCH_SERVICE", "umc-hackathon-devbox-fiq-search")
    search_endpoint = os.environ.get(
        "SEARCH_ENDPOINT", f"https://{search_service}.search.windows.net"
    )
    foundry_account = os.environ.get("FOUNDRY_ACCOUNT", "umc-hackathon-devbox-resource")
    foundry_endpoint = os.environ.get(
        "FOUNDRY_ENDPOINT", f"https://{foundry_account}.cognitiveservices.azure.com"
    )
    foundry_project = os.environ.get("FOUNDRY_PROJECT", "umc-hackathon-devbox")

    return Settings(
        subscription_id=subscription_id,
        resource_group=resource_group,
        storage_account=storage_account,
        search_service=search_service,
        search_endpoint=search_endpoint,
        foundry_account=foundry_account,
        foundry_endpoint=foundry_endpoint,
        foundry_project=foundry_project,
        data_location=os.environ.get("DATA_LOCATION", "switzerlandnorth"),
        foundry_location=os.environ.get("FOUNDRY_LOCATION", "swedencentral"),
        search_sku=os.environ.get("SEARCH_SKU", "serverless"),
        semantic_search=os.environ.get("SEMANTIC_SEARCH", "standard"),
        embedding_deployment=os.environ.get("EMBEDDING_DEPLOYMENT", "text-embedding-3-large"),
        embedding_model=os.environ.get("EMBEDDING_MODEL", "text-embedding-3-large"),
        embedding_dimensions=int(os.environ.get("EMBEDDING_DIMENSIONS", "3072")),
        embedding_sku=os.environ.get("EMBEDDING_SKU", "Standard"),
        embedding_capacity=int(os.environ.get("EMBEDDING_CAPACITY", "120")),
        chat_deployment=os.environ.get("CHAT_DEPLOYMENT", "gpt-5.6-luna"),
        chat_model=os.environ.get("CHAT_MODEL", "gpt-5.6-luna"),
        chat_sku=os.environ.get("CHAT_SKU", "GlobalStandard"),
        chat_capacity=int(os.environ.get("CHAT_CAPACITY", "500")),
        blob_container=os.environ.get("BLOB_CONTAINER", "who-guidelines"),
        data_source=os.environ.get("DATA_SOURCE", "who-guidelines-datasource"),
        search_index=os.environ.get("SEARCH_INDEX", "who-guidelines-index"),
        skillset=os.environ.get("SKILLSET", "who-guidelines-skillset"),
        indexer=os.environ.get("INDEXER", "who-guidelines-indexer"),
        semantic_config=os.environ.get("SEMANTIC_CONFIG", "who-guidelines-semantic"),
        knowledge_source=os.environ.get("KNOWLEDGE_SOURCE", "who-guidelines-ks"),
        knowledge_base=os.environ.get("KNOWLEDGE_BASE", "umc-medical-kb"),
        kb_connection_name=os.environ.get("KB_CONNECTION_NAME", "who-kb-mcp"),
        search_api_version=os.environ.get("SEARCH_API_VERSION", "2026-08-01-preview"),
        docs_dir=Path(
            os.environ.get("DOCS_DIR", str(REPO_ROOT / "labs" / "data" / "who_guidelines"))
        ),
    )


_credential: DefaultAzureCredential | None = None


def get_credential() -> DefaultAzureCredential:
    """A process-wide ``DefaultAzureCredential``, so every client shares one token cache."""
    global _credential
    if _credential is None:
        _credential = DefaultAzureCredential()
    return _credential


def search_index_client(settings: Settings):
    from azure.search.documents.indexes import SearchIndexClient

    return SearchIndexClient(
        settings.search_endpoint, get_credential(), api_version=settings.search_api_version
    )


def search_indexer_client(settings: Settings):
    from azure.search.documents.indexes import SearchIndexerClient

    return SearchIndexerClient(
        settings.search_endpoint, get_credential(), api_version=settings.search_api_version
    )


def search_client(settings: Settings, index_name: str | None = None):
    from azure.search.documents import SearchClient

    return SearchClient(
        settings.search_endpoint,
        index_name or settings.search_index,
        get_credential(),
        api_version=settings.search_api_version,
    )


def kb_retrieval_client(settings: Settings):
    from azure.search.documents.knowledgebases import KnowledgeBaseRetrievalClient

    return KnowledgeBaseRetrievalClient(
        settings.search_endpoint,
        get_credential(),
        knowledge_base_name=settings.knowledge_base,
        api_version=settings.search_api_version,
    )


# The exact set of placeholders search_objects/*.json templates use, mirroring
# the explicit var list `config.sh` used to pass to `envsubst` -- restricting
# substitution to names this pipeline owns so a stray ${...} elsewhere in a
# payload is never accidentally replaced.
def _template_values(settings: Settings) -> dict[str, str]:
    return {
        "SUBSCRIPTION_ID": settings.subscription_id,
        "RESOURCE_GROUP": settings.resource_group,
        "STORAGE_ACCOUNT": settings.storage_account,
        "STORAGE_RESOURCE_ID": settings.storage_resource_id,
        "BLOB_CONTAINER": settings.blob_container,
        "DATA_SOURCE": settings.data_source,
        "SEARCH_INDEX": settings.search_index,
        "SKILLSET": settings.skillset,
        "INDEXER": settings.indexer,
        "SEMANTIC_CONFIG": settings.semantic_config,
        "KNOWLEDGE_SOURCE": settings.knowledge_source,
        "KNOWLEDGE_BASE": settings.knowledge_base,
        "FOUNDRY_ENDPOINT": settings.foundry_endpoint,
        "EMBEDDING_DEPLOYMENT": settings.embedding_deployment,
        "EMBEDDING_MODEL": settings.embedding_model,
        "EMBEDDING_DIMENSIONS": str(settings.embedding_dimensions),
        "CHAT_DEPLOYMENT": settings.chat_deployment,
        "CHAT_MODEL": settings.chat_model,
    }


def render_template(path: Path, settings: Settings) -> dict[str, Any]:
    """Load a search-object JSON template and substitute its ``${VAR}`` placeholders.

    This replaces the old bash `render()` (an `envsubst` call): the result is a
    plain dict matching the REST wire format, which the `azure-search-documents`
    clients accept directly in place of a typed model instance.
    """
    values = _template_values(settings)
    text = path.read_text(encoding="utf-8")
    rendered = re.sub(r"\$\{(\w+)\}", lambda m: values[m.group(1)], text)
    return json.loads(rendered)


def documents_manifest() -> list[dict[str, Any]]:
    return json.loads((HERE / "documents.json").read_text(encoding="utf-8"))
