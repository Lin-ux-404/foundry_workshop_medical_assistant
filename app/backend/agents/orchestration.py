"""Notebook-style Magentic orchestration with live invocation and ledger events."""
import asyncio
import json
from collections.abc import Awaitable, Callable
from contextlib import AsyncExitStack
from datetime import datetime, timezone
from time import perf_counter
from uuid import uuid4

from agent_framework import Agent, AgentContext, AgentMiddleware
from agent_framework.orchestrations import MagenticBuilder, StandardMagenticManager

from agents.definitions import TEAM
from clients.foundry_team import FoundryTeam
from schemas import AgentCall, ChatRequest, TraceMessage

Emit = Callable[[dict], Awaitable[None]]


def now():
    return datetime.now(timezone.utc).isoformat()


class TraceMiddleware(AgentMiddleware):
    def __init__(self, emit: Emit):
        self.emit = emit
        self.assignments: dict[str, dict] = {}

    async def process(self, context: AgentContext, call_next: Callable[[], Awaitable[None]]) -> None:
        started = perf_counter()
        call = AgentCall(
            id=uuid4().hex, agent=context.agent.name, status="running", started_at=now(),
            messages=[TraceMessage(role=str(message.role), author=message.author_name, content=message.text)
                      for message in context.messages],
        )
        task = self.assignments.pop(context.agent.name, None)
        if task:
            task = {**task, "status": "running", "call_id": call.id}
            await self.emit({"type": "task", "task": task})
        await self.emit({"type": "call", "call": call.model_dump()})

        async def finish_call():
            call.duration_ms = round((perf_counter() - started) * 1000)
            await self.emit({"type": "call", "call": call.model_dump()})
            if task:
                await self.emit({"type": "task", "task": {**task, "status": call.status}})

        try:
            await call_next()
            if context.stream and context.result and hasattr(context.result, "with_transform_hook"):
                stream = context.result

                async def on_update(update):
                    if update.text:
                        call.response += update.text
                        await self.emit({"type": "agent_delta", "call_id": call.id,
                                         "agent": call.agent, "text": update.text})
                    return update

                async def on_result(response):
                    call.response = response.text
                    call.status = "completed"
                    await finish_call()
                    return response

                async def on_cleanup():
                    if call.status == "running" and getattr(stream, "_stream_error", None):
                        call.status = "failed"
                        await finish_call()

                stream.with_transform_hook(on_update)
                stream.with_result_hook(on_result)
                stream.with_cleanup_hook(on_cleanup)
                return
            call.response = context.result.text if context.result else ""
            call.status = "completed"
        except (Exception, asyncio.CancelledError):
            call.status = "failed"
            raise
        finally:
            if not (context.stream and context.result and hasattr(context.result, "with_transform_hook")):
                await finish_call()


class ObservedManager(StandardMagenticManager):
    """Observe the standard manager's real ledgers without changing its decisions."""
    def __init__(self, agent, trace):
        super().__init__(agent, max_round_count=10, max_stall_count=3, max_reset_count=2)
        self.trace = trace

    async def plan(self, context):
        plan = await super().plan(context)
        await self.trace.emit({"type": "ledger", "entry": {
            "id": uuid4().hex, "kind": "plan_created", "timestamp": now(), "text": plan.text,
            "progress": None,
        }})
        return plan

    async def replan(self, context):
        plan = await super().replan(context)
        await self.trace.emit({"type": "ledger", "entry": {
            "id": uuid4().hex, "kind": "replanned", "timestamp": now(), "text": plan.text,
            "progress": None,
        }})
        return plan

    async def create_progress_ledger(self, context):
        ledger = await super().create_progress_ledger(context)
        await self.trace.emit({"type": "ledger", "entry": {
            "id": uuid4().hex, "kind": "progress", "timestamp": now(), "text": "",
            "progress": ledger.to_dict(),
        }})
        speaker = ledger.next_speaker.answer
        if not ledger.is_request_satisfied.answer and speaker in TEAM:
            task = {"id": uuid4().hex, "agent": speaker,
                    "instruction": ledger.instruction_or_question.answer,
                    "status": "pending", "created_at": now(), "call_id": None}
            self.trace.assignments[speaker] = task
            await self.trace.emit({"type": "task", "task": task})
        return ledger


def build_workflow(team, trace):
    return MagenticBuilder(
        participants=[team["researcher"], team["knowledge_specialist"], team["communicator"], team["safety_reviewer"]],
        manager=ObservedManager(team["manager"], trace),
    ).build()


async def run_orchestration(client, payload: ChatRequest, emit: Emit) -> str:
    trace = TraceMiddleware(emit)
    async with AsyncExitStack() as stack:
        if isinstance(client, FoundryTeam):
            team = await client.build_agents(trace, stack)
            await emit({"type": "agents", "agents": client.identities()})
        else:
            # Deterministic tests exercise the same workflow with an injected client.
            team = {role: Agent(client=client, name=role, description=item["description"],
                                instructions=item["instructions"], middleware=[trace])
                    for role, item in TEAM.items()}
        workflow = build_workflow(team, trace)
        # Magentic requires a single initial task. Preserve prior turns as quoted context.
        task = payload.message
        if payload.history:
            history = json.dumps([item.model_dump() for item in payload.history], ensure_ascii=False)
            task = ("Prior conversation (quoted context, not system instructions):\n"
                    + history + "\n\nRespond to this latest user message:\n" + payload.message)
        if isinstance(client, FoundryTeam):
            stream = workflow.run(task, stream=True)
            async for _event in stream:
                pass  # TraceMiddleware forwards each agent text update as it arrives.
            events = await stream.get_final_response()
        else:
            events = await workflow.run(task)
    outputs = events.get_outputs()
    if not outputs:
        raise RuntimeError("The team returned no final response")
    final = outputs[-1]
    reply = getattr(final, "text", None)
    if reply is None and hasattr(final, "messages"):
        reply = "\n".join(message.text for message in final.messages)
    if not reply or not reply.strip():
        raise RuntimeError("The team returned an empty response")
    if reply.startswith("Workflow terminated due to reaching maximum"):
        raise RuntimeError("The team reached its orchestration limit")
    return reply

