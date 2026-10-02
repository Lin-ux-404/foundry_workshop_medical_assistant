"""Register stable prompt-agent names once, then run those exact Foundry versions."""
import asyncio
from contextlib import AsyncExitStack

from agent_framework.foundry import FoundryAgent
from azure.ai.projects.aio import AIProjectClient
from azure.ai.projects.models import (
    PromptAgentDefinition,
    WebSearchTool,
)
from azure.core.exceptions import HttpResponseError, ResourceNotFoundError

from agents.definitions import TEAM
from config import get_settings


class FoundrySetupError(RuntimeError):
    """Safe actionable setup error; never includes endpoint or credential values."""


class FoundryTeam:
    FIXED_AGENT_VERSIONS = {"knowledge_specialist": "2"}

    def __init__(self, credential):
        self.settings = get_settings()
        self.credential = credential
        self.project = AIProjectClient(endpoint=self.settings.azure_ai_project_endpoint, credential=credential)
        self.versions: dict[str, str] = {}
        self.lock = asyncio.Lock()

    def identities(self):
        return [{"id": role, "name": item["name"], "version": self.versions.get(role),
                 "registered": role in self.versions} for role, item in TEAM.items()]

    async def register_version(self, role, item, tools):
        try:
            created = await self.project.agents.create_version(
                agent_name=item["name"], description=item["description"],
                definition=PromptAgentDefinition(model=self.settings.azure_ai_model_deployment_name,
                                                 instructions=item["instructions"], tools=tools),
                metadata={"application": "medical-assistant-workshop", "role": role},
            )
            return str(created.version)
        except HttpResponseError as error:
            raise FoundrySetupError(
                f"Foundry could not register {item['name']} (HTTP {error.status_code}). "
                "Check that the project endpoint and model deployment exist, and that your identity "
                "can create agent versions."
            ) from error

    async def tools_for(self, role):
        if role == "researcher":
            return [WebSearchTool(search_context_size="medium")]
        return []

    async def resolve(self):
        async with self.lock:
            if len(self.versions) == len(TEAM):
                return
            available = [deployment.name async for deployment in self.project.deployments.list()]
            if self.settings.azure_ai_model_deployment_name not in available:
                raise FoundrySetupError(
                    "The configured model deployment does not exist in this Foundry project. "
                    "Set AZURE_AI_MODEL_DEPLOYMENT_NAME to an existing chat deployment and restart the backend."
                )
            for role, fixed_version in self.FIXED_AGENT_VERSIONS.items():
                item = TEAM[role]
                try:
                    await self.project.agents.get_version(
                        agent_name=item["name"], agent_version=fixed_version
                    )
                except ResourceNotFoundError as error:
                    raise FoundrySetupError(
                        f"The required Foundry agent {item['name']} version {fixed_version} was not found. "
                        "Create or publish that version in the configured project."
                    ) from error
            for role, item in TEAM.items():
                if role in self.versions:
                    continue
                fixed_version = self.FIXED_AGENT_VERSIONS.get(role)
                if fixed_version:
                    self.versions[role] = fixed_version
                    continue
                tools = await self.tools_for(role)
                try:
                    existing = await self.project.agents.get(item["name"])
                    latest = existing.versions.latest
                    version = str(latest.version)
                    definition = latest.definition
                    changed = (getattr(definition, "model", None) != self.settings.azure_ai_model_deployment_name
                               or getattr(definition, "instructions", None) != item["instructions"]
                               or self._tool_signature(getattr(definition, "tools", None)) != self._tool_signature(tools))
                    if changed:
                        if (latest.metadata or {}).get("application") != "medical-assistant-workshop":
                            raise FoundrySetupError(
                                f"The existing {item['name']} has a different definition and is not owned by this app. "
                                "Use a different team name or resolve the definition in Foundry."
                            )
                        # A new version preserves the prior deployment and its history.
                        version = await self.register_version(role, item, tools)
                except ResourceNotFoundError:
                    version = await self.register_version(role, item, tools)
                self.versions[role] = version

    @staticmethod
    def _tool_signature(tools):
        return tuple(sorted(str(tool.as_dict(exclude_readonly=True)) for tool in (tools or [])))

    async def build_agents(self, trace, stack: AsyncExitStack):
        await self.resolve()
        result = {}
        for role, item in TEAM.items():
            result[role] = await stack.enter_async_context(FoundryAgent(
                project_endpoint=self.settings.azure_ai_project_endpoint,
                agent_name=item["name"], agent_version=self.versions[role],
                credential=self.credential, name=role, description=item["description"],
                allow_preview=False, timeout=self.settings.orchestration_timeout_seconds,
                middleware=[trace],
            ))
        return result

    async def close(self):
        await self.project.close()
