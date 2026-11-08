import pytest
from pydantic import ValidationError

from app.schemas import EmailSendArguments, ToolCallRequest


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
