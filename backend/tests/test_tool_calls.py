from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)
URL = "/api/v1/tool-calls"

def make_payload(**overrides):
    payload = {
        "request_id": "req-1",
        "agent_id": "assistant_2",
        "user_id": "user-1",
        "session_id": "session-1",
        "original_goal": "Send the weekly report",
        "tool": "email.send",
        "arguments": {
            "recipient": "alex@example.com",
            "subject": "Weekly report",
            "body": "Report attached.",
        },
    }
    payload.update(overrides)
    return payload

def email_arguments(**overrides):
    arguments = {
        "recipient": "alex@example.com",
        "subject": "Weekly report",
        "body": "Report attached.",
    }
    arguments.update(overrides)
    return arguments

def test_internal_email_is_allowed():
    response = client.post(URL, json=make_payload())
    assert response.status_code == 200
    body = response.json()
    assert body["decision"] == "allow"
    assert body["approval_status"] == "not_required"
    assert body["request_id"] == "req-1"
    assert body["agent_id"] == "assistant_2"
    assert body["tool"] == "email.send"
    assert body["reason"]
    assert "timestamp" in body

def test_denied_domain_is_blocked():
    payload = make_payload(arguments=email_arguments(recipient="bob@example.net"))
    response = client.post(URL, json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["decision"] == "block"
    assert body["approval_status"] == "not_required"

def test_external_email_requires_approval():
    payload = make_payload(arguments=email_arguments(recipient="carol@example.org"))
    response = client.post(URL, json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["decision"] == "approval_required"
    assert body["approval_status"] == "pending"

def test_unknown_agent_is_blocked():
    response = client.post(URL, json=make_payload(agent_id="intruder"))
    assert response.status_code == 200
    body = response.json()
    assert body["decision"] == "block"
    assert body["approval_status"] == "not_required"

def test_unsupported_tool_is_blocked():
    payload = make_payload(tool="calendar.delete", arguments={"event_id": "42"})
    response = client.post(URL, json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["decision"] == "block"
    assert body["approval_status"] == "not_required"

def test_invalid_email_arguments_return_422():
    payload = make_payload(arguments=email_arguments(recipient="not-an-email"))
    response = client.post(URL, json=payload)
    assert response.status_code == 422
    errors = response.json()["detail"]
    assert errors[0]["loc"] == ["body", "arguments", "recipient"]
    assert all("input" not in error for error in errors)

def test_missing_email_subject_returns_422():
    arguments = email_arguments()
    del arguments["subject"]
    response = client.post(URL, json=make_payload(arguments=arguments))
    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["body", "arguments", "subject"]

def test_extra_email_argument_returns_422():
    payload = make_payload(arguments=email_arguments(cc="boss@example.com"))
    response = client.post(URL, json=payload)
    assert response.status_code == 422

def test_missing_top_level_field_returns_422():
    payload = make_payload()
    del payload["request_id"]
    response = client.post(URL, json=payload)
    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["body", "request_id"]