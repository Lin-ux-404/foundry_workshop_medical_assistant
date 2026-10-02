"""Verify registration without connecting to Azure or reading environment files."""
import asyncio
import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from azure.core.exceptions import ResourceNotFoundError
from clients.foundry_team import FoundrySetupError, FoundryTeam
from agents.definitions import TEAM


async def available():
    yield SimpleNamespace(name="test-model")


async def search_connections():
    yield SimpleNamespace(id="search-connection-id", target="https://search.test")


def make_project(get):
    return SimpleNamespace(
        agents=SimpleNamespace(get=get, get_version=AsyncMock(return_value=SimpleNamespace(version="2")),
                               create_version=AsyncMock(return_value=SimpleNamespace(version="2"))),
        deployments=SimpleNamespace(list=available), close=AsyncMock(),
        connections=SimpleNamespace(list=lambda **_: search_connections()),
    )


def existing(role, model="test-model", owner="medical-assistant-workshop", tools=None):
    return SimpleNamespace(versions=SimpleNamespace(latest=SimpleNamespace(
        version="1", definition=SimpleNamespace(model=model, instructions=TEAM[role]["instructions"], tools=tools),
        metadata={"application": owner},
    )))


class RegistrationTests(unittest.IsolatedAsyncioTestCase):
    def team(self, project):
        settings = SimpleNamespace(azure_ai_project_endpoint="https://test.invalid/api/projects/test",
                                   azure_ai_model_deployment_name="test-model",
                                   azure_ai_search_connection_name="",
                                   azure_ai_search_endpoint="https://search.test",
                                   azure_ai_search_index_name="who")
        with patch("clients.foundry_team.get_settings", return_value=settings), patch("clients.foundry_team.AIProjectClient", return_value=project):
            return FoundryTeam(object())

    async def test_missing_agents_are_created_once_and_names_are_reported(self):
        project = make_project(AsyncMock(side_effect=ResourceNotFoundError()))
        team = self.team(project)
        await asyncio.gather(team.resolve(), team.resolve())
        self.assertEqual(project.agents.create_version.await_count, 4)
        self.assertEqual(project.agents.get.await_count, 4)
        project.agents.get_version.assert_awaited_once_with(
            agent_name="medical-assistant-who-knowledge", agent_version="2")
        self.assertEqual([item["name"] for item in team.identities()], [item["name"] for item in TEAM.values()])
        self.assertEqual(len(team.identities()), 5)
        self.assertTrue(all(item["registered"] for item in team.identities()))
        versions = {item["id"]: item["version"] for item in team.identities()}
        self.assertEqual(versions["knowledge_specialist"], "2")
        self.assertTrue(all(version == "2" for role, version in versions.items() if role != "knowledge_specialist"))
        for call in project.agents.create_version.await_args_list:
            self.assertEqual(call.kwargs["definition"].model, "test-model")
        definitions = {call.kwargs["agent_name"]: call.kwargs["definition"]
                      for call in project.agents.create_version.await_args_list}
        self.assertEqual([tool.type for tool in definitions[TEAM["researcher"]["name"]].tools], ["web_search"])
        self.assertNotIn(TEAM["knowledge_specialist"]["name"], definitions)
        await team.close()
        project.close.assert_awaited_once()

    async def test_matching_versions_are_reused_without_mutation(self):
        get = AsyncMock()
        project = make_project(get)
        team = self.team(project)
        get.side_effect = [existing(role, tools=await team.tools_for(role)) for role in TEAM
                           if role != "knowledge_specialist"]
        await team.resolve()
        project.agents.create_version.assert_not_awaited()
        versions = {item["id"]: item["version"] for item in team.identities()}
        self.assertEqual(versions["knowledge_specialist"], "2")
        self.assertTrue(all(version == "1" for role, version in versions.items() if role != "knowledge_specialist"))

    async def test_model_change_creates_new_versions_for_our_agents(self):
        project = make_project(AsyncMock(side_effect=[existing(role, model="old-model") for role in TEAM]))
        team = self.team(project)
        await team.resolve()
        self.assertEqual(project.agents.create_version.await_count, 4)
        self.assertTrue(all(item["version"] == "2" for item in team.identities()))

    async def test_unowned_definitions_are_not_modified(self):
        project = make_project(AsyncMock(return_value=existing("manager", model="old-model", owner="someone-else")))
        with self.assertRaises(FoundrySetupError):
            await self.team(project).resolve()
        project.agents.create_version.assert_not_awaited()

    async def test_permission_failure_does_not_create_agents(self):
        project = make_project(AsyncMock(side_effect=PermissionError()))
        with self.assertRaises(PermissionError):
            await self.team(project).resolve()
        project.agents.create_version.assert_not_awaited()

    async def test_missing_preconfigured_who_agent_version_fails_clearly(self):
        project = make_project(AsyncMock(side_effect=ResourceNotFoundError()))
        project.agents.get_version.side_effect = ResourceNotFoundError()
        with self.assertRaisesRegex(FoundrySetupError, "medical-assistant-who-knowledge version 2"):
            await self.team(project).resolve()
        project.agents.create_version.assert_not_awaited()
