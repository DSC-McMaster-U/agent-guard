from datetime import datetime, timezone
import psycopg
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.schemas import ToolCallSummary
from app.storage import DuplicateRequestError

VALID_BODY = {
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

@pytest.fixture
def client():
    return TestClient(app)

def test_save_success(client, monkeypatch):
    saved = []
    monkeypatch.setattr(
        "app.main.save_summary", lambda connection, summary: saved.append(summary)
    )
    response = client.post("/api/v1/tool-calls", json=VALID_BODY)
    assert response.status_code == 200
    assert len(saved) == 1
    assert saved[0].request_id == "req-1"
    assert response.json()["request_id"] == "req-1"

def test_duplicate_returns_409(client, monkeypatch):
    def raise_duplicate(connection, summary):
        raise DuplicateRequestError(summary.request_id)

    monkeypatch.setattr("app.main.save_summary", raise_duplicate)
    response = client.post("/api/v1/tool-calls", json=VALID_BODY)
    assert response.status_code == 409

def test_unavailable_returns_503_without_details(client, monkeypatch):
    def raise_unavailable(connection, summary):
        raise psycopg.OperationalError("secret details")

    monkeypatch.setattr("app.main.save_summary", raise_unavailable)
    response = client.post("/api/v1/tool-calls", json=VALID_BODY)
    assert response.status_code == 503
    assert "secret" not in response.text

def test_invalid_email_returns_422_and_does_not_save(client, monkeypatch):
    saved = []
    monkeypatch.setattr(
        "app.main.save_summary", lambda connection, summary: saved.append(summary)
    )
    body = {
        **VALID_BODY,
        "arguments": {**VALID_BODY["arguments"], "recipient": "not-an-email"},
    }
    response = client.post("/api/v1/tool-calls", json=body)
    assert response.status_code == 422
    assert saved == []

def test_list_empty(client):
    response = client.get("/api/v1/tool-calls")
    assert response.status_code == 200
    assert response.json() == []

def test_list_returns_summaries(client, monkeypatch):
    summary = ToolCallSummary(
        request_id="req-1",
        agent_id="assistant_2",
        tool="email.send",
        arguments=VALID_BODY["arguments"],
        decision="allow",
        reason="Recipient is inside the organization.",
        timestamp=datetime(2026, 11, 3, 18, 0, tzinfo=timezone.utc),
        approval_status="not_required",
    )
    monkeypatch.setattr(
        "app.main.list_summaries", lambda connection, limit=20: [summary]
    )
    response = client.get("/api/v1/tool-calls")
    assert response.status_code == 200
    assert [item["request_id"] for item in response.json()] == ["req-1"]

def test_list_unavailable_returns_503(client, monkeypatch):
    def raise_unavailable(connection, limit=20):
        raise psycopg.OperationalError("secret details")

    monkeypatch.setattr("app.main.list_summaries", raise_unavailable)
    response = client.get("/api/v1/tool-calls")
    assert response.status_code == 503

def test_health_does_not_need_the_database(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}