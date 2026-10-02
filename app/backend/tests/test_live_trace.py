"""Verify agent output deltas are forwarded while a streaming call is consumed."""
import unittest
from types import SimpleNamespace

from agent_framework import AgentResponse, AgentResponseUpdate, Content, ResponseStream

from agents.orchestration import TraceMiddleware


class LiveTraceTests(unittest.IsolatedAsyncioTestCase):
    async def test_agent_tokens_are_emitted_before_the_call_completes(self):
        events = []

        async def emit(event):
            events.append(event)

        updates = [
            AgentResponseUpdate(contents=[Content.from_text("Live ")], role="assistant"),
            AgentResponseUpdate(contents=[Content.from_text("answer")], role="assistant"),
        ]
        async def updates_stream():
            for update in updates:
                yield update

        context = SimpleNamespace(
            agent=SimpleNamespace(name="researcher"), messages=[], stream=True, result=None,
        )
        middleware = TraceMiddleware(emit)

        async def call_next():
            context.result = ResponseStream(updates_stream(), finalizer=AgentResponse.from_updates)

        await middleware.process(context, call_next)
        async for _ in context.result:
            pass
        result = await context.result.get_final_response()

        deltas = [event["text"] for event in events if event["type"] == "agent_delta"]
        final_call = [event["call"] for event in events if event["type"] == "call"][-1]
        self.assertEqual(deltas, ["Live ", "answer"])
        self.assertEqual(result.text, "Live answer")
        self.assertEqual(final_call["response"], "Live answer")
        self.assertEqual(final_call["status"], "completed")
