import pytest
from app.database import get_connection
from app.main import app

class FakeConnection:
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc, traceback):
        return False
    def close(self):
        pass

@pytest.fixture(autouse=True)
def fake_database(monkeypatch):
    app.dependency_overrides[get_connection] = lambda: FakeConnection()
    monkeypatch.setattr("app.main.save_summary", lambda connection, summary: None)
    monkeypatch.setattr("app.main.list_summaries", lambda connection, limit=20: [])
    yield
    app.dependency_overrides.clear()