from fastapi.testclient import TestClient # type: ignore
from app.main import app

client = TestClient(app)

def test_root_returns_message():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data == {"message": "Hello from FastAPI (via router)"}
