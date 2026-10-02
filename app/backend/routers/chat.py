"""Chat endpoints: compatible JSON response and live newline-delimited traces."""
import asyncio
import json
import logging
import re
from contextlib import suppress

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from azure.core.exceptions import ClientAuthenticationError

from agents.orchestration import run_orchestration
from clients.foundry_team import FoundrySetupError
from config import get_settings
from schemas import AgentCall, ChatRequest, ChatResponse

router = APIRouter(prefix="/api", tags=["patient"])
logger = logging.getLogger(__name__)


def require_client(request: Request):
    client = request.app.state.foundry_client
    if client is None:
        raise HTTPException(503, "Live chat needs Azure configuration. Set AZURE_AI_PROJECT_ENDPOINT "
                            "and AZURE_AI_MODEL_DEPLOYMENT_NAME in app/backend/.env, then restart the backend. "
                            "Conversation activity will appear after a live request.")
    return client


def error_message(error: Exception) -> str:
    if isinstance(error, FoundrySetupError):
        return str(error)
    if isinstance(error, TimeoutError):
        return "The team took too long to respond. Please try again with a shorter question."
    # Don't expose credentials, provider responses, or patient input in errors/logs.
    cause = error
    for _ in range(5):
        if cause.__cause__ is None:
            break
        cause = cause.__cause__
    if isinstance(cause, ClientAuthenticationError):
        # Azure CLI errors can include account identifiers and other diagnostics.
        # Classify the failure without returning or logging the provider's message.
        details = str(cause).casefold()
        if "az login" in details or "not logged in" in details:
            logger.warning("Azure CLI could not provide an access token (login unavailable)")
            return ("The backend could not access an Azure CLI sign-in. Confirm that the signed-in CLI "
                    "session is available to the same Windows user and process that launched the backend, "
                    "then restart it.")
        if "not installed" in details or "not found" in details or "executable" in details:
            logger.warning("Azure CLI executable is unavailable to the backend")
            return "The Azure CLI executable is unavailable on the backend's PATH. Restart the backend from a shell where az is available."
        match = re.search(r"AADSTS\d+", str(cause), re.IGNORECASE)
        if match:
            logger.warning("Azure CLI token acquisition failed (%s)", match.group(0).upper())
            return (f"The Azure CLI sign-in was rejected ({match.group(0).upper()}). "
                    "Check the signed-in tenant and account in the shell that launches the backend.")
        logger.warning("Azure CLI could not acquire a Foundry access token")
        return ("The backend could not acquire a Foundry access token from Azure CLI. "
                "Check the Azure CLI sign-in and tenant available to the backend process.")
    # Only structured error identifiers are exposed, never provider message bodies.
    fields = [type(cause).__name__, str(getattr(cause, "status_code", "")),
              str(getattr(cause, "code", "")), str(getattr(cause, "param", ""))]
    safe = ", ".join(value for value in fields if value and value != "None"
                     and re.fullmatch(r"[\w.\[\]-]{1,100}", value))
    logger.warning("Orchestration failed (%s)", safe)
    return (f"The care team could not finish this request ({safe}). "
            "Check the backend's Azure configuration and credentials, then try again.")


@router.post("/chat", response_model=ChatResponse)
async def chat(payload: ChatRequest, request: Request) -> ChatResponse:
    client = require_client(request)
    calls: dict[str, AgentCall] = {}

    async def collect(event: dict):
        if event["type"] == "call":
            call = AgentCall.model_validate(event["call"])
            calls[call.id] = call

    try:
        async with asyncio.timeout(get_settings().orchestration_timeout_seconds):
            reply = await run_orchestration(client, payload, collect)
        return ChatResponse(reply=reply, calls=list(calls.values()))
    except Exception as error:
        raise HTTPException(504 if isinstance(error, TimeoutError) else 502, error_message(error)) from error


@router.post("/chat/stream")
async def chat_stream(payload: ChatRequest, request: Request) -> StreamingResponse:
    client = require_client(request)

    async def stream():
        queue: asyncio.Queue[dict | None] = asyncio.Queue()

        async def execute():
            try:
                async with asyncio.timeout(get_settings().orchestration_timeout_seconds):
                    reply = await run_orchestration(client, payload, queue.put)
                await queue.put({"type": "reply", "reply": reply})
            except Exception as error:
                await queue.put({"type": "error", "message": error_message(error)})
            finally:
                await queue.put(None)

        task = asyncio.create_task(execute())
        try:
            while True:
                try:
                    event = await asyncio.wait_for(queue.get(), timeout=1)
                except TimeoutError:
                    # Keep the stream responsive and stop model work on disconnect.
                    if await request.is_disconnected():
                        break
                    yield "\n"
                    continue
                if event is None:
                    break
                yield json.dumps(event, ensure_ascii=False) + "\n"
        finally:
            task.cancel()
            with suppress(asyncio.CancelledError):
                await task

    return StreamingResponse(stream(), media_type="application/x-ndjson",
                             headers={"Cache-Control": "no-store", "X-Accel-Buffering": "no"})
