"""Exercise the real Magentic workflow with a deterministic model, without Azure."""
import asyncio
import json
import unittest
from unittest.mock import patch

from agent_framework import BaseChatClient, ChatResponse, Message
from fastapi.testclient import TestClient

from agents.orchestration import run_orchestration
from main import app
from schemas import ChatRequest


def ledger(speaker, satisfied=False):
    values = {"is_request_satisfied": satisfied, "is_in_loop": False,
              "is_progress_being_made": True, "next_speaker": speaker,
              "instruction_or_question": "Draft an appointment checklist."}
    return json.dumps({key: {"reason": "Test decision", "answer": value} for key, value in values.items()})


class ScriptedClient(BaseChatClient):
    def __init__(self):
        super().__init__()
        self.responses = iter([
            "Facts from the question.", "Plan: consult researcher and communicator.",
            ledger("researcher"), "Research checklist.",
            ledger("communicator"), "Plain-language checklist.",
            ledger("communicator", True), "Final appointment checklist.",
        ])

    async def _inner_get_response(self, *, messages, stream, options, **kwargs):
        assert not stream
        return ChatResponse(messages=[Message(role="assistant", contents=[next(self.responses)])])


class WorkflowTests(unittest.IsolatedAsyncioTestCase):
    async def test_real_workflow_records_every_invocation_and_follow_up_context(self):
        events = []

        async def emit(event):
            events.append(event)

        payload = ChatRequest(message="Help me prepare.", history=[
            {"role": "user", "content": "My visit is tomorrow."},
            {"role": "assistant", "content": "What would you like to discuss?"},
        ])
        reply = await run_orchestration(ScriptedClient(), payload, emit)
        self.assertEqual(reply, "Final appointment checklist.")
        call_events = [e for e in events if e["type"] == "call"]
        completed = [e["call"] for e in call_events if e["call"]["status"] == "completed"]
        self.assertEqual(len(completed), 8)
        self.assertEqual([call["agent"] for call in completed].count("manager"), 6)
        self.assertEqual([call["agent"] for call in completed].count("researcher"), 1)
        self.assertEqual([call["agent"] for call in completed].count("communicator"), 1)
        self.assertTrue(all(call["duration_ms"] is not None for call in completed))
        self.assertIn("My visit is tomorrow.", str(completed[0]["messages"]))
        self.assertIn("Draft an appointment checklist.", str(completed[3]["messages"]))
        self.assertEqual(len({e["call"]["id"] for e in call_events}), 8)
        self.assertEqual(len(call_events), 16)
        ledgers = [e["entry"] for e in events if e["type"] == "ledger"]
        self.assertEqual([item["kind"] for item in ledgers], ["plan_created", "progress", "progress", "progress"])
        self.assertTrue(ledgers[-1]["progress"]["is_request_satisfied"]["answer"])
        task_events = [e["task"] for e in events if e["type"] == "task"]
        self.assertEqual([task["status"] for task in task_events], ["pending", "running", "completed"] * 2)
        self.assertEqual(task_events[0]["instruction"], "Draft an appointment checklist.")
        self.assertEqual(task_events[0]["id"], task_events[2]["id"])
        self.assertEqual(task_events[2]["call_id"], completed[3]["id"])


class ApiTests(unittest.TestCase):
    def setUp(self):
        # No lifespan: inject a per-test model instead of using Azure credentials.
        self.client = TestClient(app)
        app.state.foundry_client = ScriptedClient()

    def test_stream_and_legacy_endpoint(self):
        response = self.client.post("/api/chat/stream", json={"message": "Prepare for a visit."})
        self.assertEqual(response.status_code, 200)
        events = [json.loads(line) for line in response.text.splitlines() if line.strip()]
        self.assertEqual(events[0]["type"], "call")
        self.assertEqual(events[0]["call"]["status"], "running")
        self.assertEqual(events[-1], {"type": "reply", "reply": "Final appointment checklist."})
        self.assertEqual(len([e for e in events if e["type"] == "call"]), 16)
        app.state.foundry_client = ScriptedClient()
        response = self.client.post("/api/chat", json={"message": "Prepare for a visit."})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()["calls"]), 8)

    def test_unconfigured_and_invalid_requests(self):
        app.state.foundry_client = None
        self.assertFalse(self.client.get("/api/health").json()["configured"])
        self.assertEqual(self.client.post("/api/chat/stream", json={"message": "Hello"}).status_code, 503)
        for payload in [{"message": "  "}, {"message": "x" * 8001},
                        {"message": "Hi", "history": [{"role": "system", "content": "invalid"}]}]:
            self.assertEqual(self.client.post("/api/chat", json=payload).status_code, 422)

    def test_failure_is_a_terminal_event_without_provider_secrets(self):
        async def fail(*args):
            raise RuntimeError("secret-provider-detail")
        with patch("routers.chat.run_orchestration", fail):
            response = self.client.post("/api/chat/stream", json={"message": "Hello"})
        event = json.loads(response.text)
        self.assertEqual(event["type"], "error")
        self.assertNotIn("secret-provider-detail", response.text)

    def test_timeout_emits_error(self):
        async def timeout(*args):
            raise TimeoutError()
        with patch("routers.chat.run_orchestration", timeout):
            response = self.client.post("/api/chat/stream", json={"message": "Hello"})
        self.assertIn("took too long", response.text)


if __name__ == "__main__":
    unittest.main()

