from typing import Any, Literal

from pydantic import AwareDatetime, BaseModel, EmailStr, Field

from app.policy import Decision


class TriggerSource(BaseModel):
    type: Literal[
        "user_instruction",
        "untrusted_email_body",
        "untrusted_webpage",
        "untrusted_document",
        "tool_result",
        "unknown",
    ] = "unknown"
    content: str = Field(default="", max_length=10000)
    trust_level: Literal["trusted", "untrusted", "unknown"] = "unknown"


class ToolCallRequest(BaseModel):
    model_config = {"extra": "forbid"}

    request_id: str = Field(min_length=1, max_length=128)
    agent_id: str = Field(min_length=1, max_length=128)
    user_id: str = Field(min_length=1, max_length=128)
    session_id: str = Field(min_length=1, max_length=128)
    original_goal: str = Field(min_length=1, max_length=4000)
    tool: str = Field(min_length=1, max_length=128)
    arguments: dict[str, Any]
    trigger_source: TriggerSource | None = Field(default_factory=TriggerSource)


class EmailSendArguments(BaseModel):
    model_config = {"extra": "forbid"}

    recipient: EmailStr
    subject: str = Field(min_length=1, max_length=200)
    body: str = Field(min_length=1, max_length=10000)


class ToolCallSummary(BaseModel):
    model_config = {"extra": "forbid"}

    request_id: str
    agent_id: str
    tool: str
    arguments: dict[str, Any]
    decision: Decision
    reason: str
    timestamp: AwareDatetime
    approval_status: Literal["not_required", "pending", "approved", "denied"]
