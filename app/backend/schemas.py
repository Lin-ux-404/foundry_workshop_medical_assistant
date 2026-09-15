"""Patient chat request and response models."""

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(..., description="The patient's message to the assistant.")


class ChatResponse(BaseModel):
    reply: str
