import pytest
from fastapi.testclient import TestClient

from app.database import get_connection
from app.main import app


@pytest.mark.parametrize("database_url", [None, "", "   "])
def test_missing_database_config_does_not_attempt_default_connection(monkeypatch, database_url):
    app.dependency_overrides.pop(get_connection, None)
    if database_url is None:
        monkeypatch.delenv("DATABASE_URL", raising=False)
    else:
        monkeypatch.setenv("DATABASE_URL", database_url)

    def unexpected_connection(*args, **kwargs):
        raise AssertionError("Missing config must not fall back to a default database")

    monkeypatch.setattr("app.database.psycopg.connect", unexpected_connection)
    with TestClient(app) as client:
        response = client.get("/api/v1/tool-calls")
    assert response.status_code == 503
    assert response.json() == {"detail": "Database unavailable"}


def test_malformed_database_config_is_a_generic_503(monkeypatch):
    app.dependency_overrides.pop(get_connection, None)
    monkeypatch.setenv("DATABASE_URL", "not a connection string secret-value")
    with TestClient(app) as client:
        response = client.get("/api/v1/tool-calls")
        health = client.get("/health")
    assert response.status_code == 503
    assert response.json() == {"detail": "Database unavailable"}
    assert "secret-value" not in response.text
    assert health.status_code == 200
