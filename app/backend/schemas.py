"""Pydantic models: API request/response contracts and structured agent output.

Structured outputs are the point of `TriageResult`: the Triage Agent is asked
to return THIS schema instead of free text, so downstream workflows can rely on
predictable fields. This is an educational demo and never a medical diagnosis.
"""
from enum import Enum

from pydantic import BaseModel, Field


# --------- Patient chat ---------
class ChatRequest(BaseModel):
    message: str = Field(..., description="The patient's message to the assistant.")


class ChatResponse(BaseModel):
    reply: str


# --------- Structured triage output ---------
class SeverityLevel(str, Enum):
    self_care = "self_care"
    routine_appointment = "routine_appointment"
    priority_appointment = "priority_appointment"
    immediate_escalation = "immediate_escalation"


class TriageResult(BaseModel):
    """Structured, non-diagnostic triage assessment produced by the Triage Agent."""

    severity: SeverityLevel = Field(..., description="Configurable demo severity category.")
    recommendation: str = Field(..., description="Short, non-diagnostic next-step recommendation.")
    escalate: bool = Field(..., description="True if the case needs professional / emergency support.")
    reasoning: str = Field(..., description="Brief explanation of the assessment.")
    missing_information: list[str] = Field(
        default_factory=list, description="Fields still needed for a complete assessment."
    )


class TriageRequest(BaseModel):
    message: str = Field(..., description="Free-text symptom description from the patient.")
