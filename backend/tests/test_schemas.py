from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from app.schemas import EmailSendArguments, ToolCallRequest, ToolCallSummary


def valid_request():
    return {
        "request_id": "req_1",
        "agent_id": "assistant_2",
        "user_id": "user_13",
        "session_id": "session_2",
        "original_goal": "Send the approved report to the project lead",
        "tool": "email.send",
        "arguments": {
            "recipient": "lead@example.com",
            "subject": "Approved Report",
            "body": "Hi, please see the report attached.",
        },
    }


def test_valid_request_is_accepted():
    request = ToolCallRequest(**valid_request())
    assert request.user_id == "user_13"


def test_missing_user_id_is_rejected():
    data = valid_request()
    del data["user_id"]
    with pytest.raises(ValidationError):
        ToolCallRequest(**data)


def test_non_object_arguments_is_rejected():
    data = valid_request()
    data["arguments"] = "send an email"
    with pytest.raises(ValidationError):
        ToolCallRequest(**data)


def test_invalid_email_is_rejected():
    with pytest.raises(ValidationError):
        EmailSendArguments(
            recipient="not-an-email",
            subject="Approved Report",
            body="Hi, please see the report attached.",
        )


def test_missing_trigger_source_is_not_trusted():
    request = ToolCallRequest(**valid_request())
    assert request.trigger_source.trust_level == "unknown"


def test_extra_email_key_is_rejected():
    with pytest.raises(ValidationError):
        EmailSendArguments(
            recipient="lead@example.com",
            subject="Approved Report",
            body="Hi, please see the report attached.",
            cc="someone@example.com",
        )


def valid_summary():
    return {
        "request_id": "req_1",
        "agent_id": "assistant_2",
        "tool": "email.send",
        "arguments": {
            "recipient": "teammate@example.com",
            "subject": "Hi",
            "body": "Hello",
        },
        "decision": "allow",
        "reason": "Recipient is inside the organization.",
        "timestamp": datetime(2026, 11, 3, 18, 0, tzinfo=timezone.utc),
        "approval_status": "not_required",
    }


def test_valid_summary_serializes_to_frontend_json():
    summary = ToolCallSummary(**valid_summary())
    data = summary.model_dump(mode="json")
    assert data["timestamp"] == "2026-11-03T18:00:00Z"
    assert data["decision"] == "allow"
    assert list(data) == [
        "request_id", "agent_id", "tool", "arguments",
        "decision", "reason", "timestamp", "approval_status",
    ]


def test_invalid_decision_is_rejected():
    data = valid_summary()
    data["decision"] = "maybe"
    with pytest.raises(ValidationError):
        ToolCallSummary(**data)


def test_invalid_approval_status_is_rejected():
    data = valid_summary()
    data["approval_status"] = "unknown"
    with pytest.raises(ValidationError):
        ToolCallSummary(**data)
