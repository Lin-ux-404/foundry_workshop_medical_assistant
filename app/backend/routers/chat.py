"""Patient chat endpoint."""
from fastapi import APIRouter, Request

from agents import build_patient_assistant
from schemas import ChatRequest, ChatResponse

router = APIRouter(prefix="/api", tags=["patient"])


@router.post("/chat", response_model=ChatResponse)
async def chat(payload: ChatRequest, request: Request) -> ChatResponse:
    client = request.app.state.foundry_client
    agent = build_patient_assistant(client)
    result = await agent.run(payload.message)
    return ChatResponse(reply=result.text)
