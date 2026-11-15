from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_unknown_path_404_check():
    response = client.get("/does-not-exist")
    assert response.status_code == 404
    assert response.json() == {"detail": "Not Found"}