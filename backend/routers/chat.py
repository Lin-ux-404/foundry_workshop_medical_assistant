"""Patient-facing endpoints.

- POST /api/chat    -> free-text conversational reply (Patient Assistant)
- POST /api/triage  -> STRUCTURED, non-diagnostic assessment (Triage Agent)

The triage endpoint shows the structured-output pattern: we ask the agent to
return the `TriageResult` schema and read `result.value`. A small fallback
parses the raw text in case a given Foundry runtime does not honour
`response_format` for server-side agents.
"""
from fastapi import APIRouter, HTTPException, Request

from agents import build_patient_assistant, build_triage_agent
from schemas import ChatRequest, ChatResponse, TriageRequest, TriageResult

router = APIRouter(prefix="/api", tags=["patient"])


@router.post("/chat", response_model=ChatResponse)
async def chat(payload: ChatRequest, request: Request) -> ChatResponse:
    client = request.app.state.foundry_client
    agent = build_patient_assistant(client)
    result = await agent.run(payload.message)
    return ChatResponse(reply=result.text)


@router.post("/triage", response_model=TriageResult)
async def triage(payload: TriageRequest, request: Request) -> TriageResult:
    client = request.app.state.foundry_client
    agent = build_triage_agent(client)
    result = await agent.run(payload.message, response_format=TriageResult)

    # Preferred path: the framework already parsed the structured output.
    if result.value is not None:
        return result.value

    # Fallback: parse the raw JSON text ourselves.
    try:
        return TriageResult.model_validate_json(result.text)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(
            status_code=502,
            detail=f"Could not parse structured triage output: {exc}",
        )
