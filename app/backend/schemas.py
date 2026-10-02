"""Validated chat payloads and request-scoped agent traces."""
from typing import Annotated, Literal

from pydantic import BaseModel, Field, StringConstraints, model_validator

Text = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=8000)]


class HistoryMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: Text


class ChatRequest(BaseModel):
    message: Text
    history: list[HistoryMessage] = Field(default_factory=list, max_length=40)

    @model_validator(mode="after")
    def bound_context(self):
        if sum(len(item.content) for item in self.history) + len(self.message) > 80000:
            raise ValueError("Conversation is too long. Please start a new conversation.")
        return self


class TraceMessage(BaseModel):
    role: str
    author: str | None = None
    content: str


class AgentCall(BaseModel):
    id: str
    agent: Literal["manager", "researcher", "communicator", "knowledge_specialist", "safety_reviewer"]
    status: Literal["running", "completed", "failed"]
    started_at: str
    duration_ms: int | None = None
    messages: list[TraceMessage]
    response: str = ""


class ChatResponse(BaseModel):
    reply: str
    calls: list[AgentCall] = Field(default_factory=list)
