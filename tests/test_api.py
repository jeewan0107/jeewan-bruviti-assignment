from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_home():
    response = client.get("/")
    assert response.status_code == 200
    assert "Repair vs Replace" in response.text

def test_decide(case):
    response = client.post("/decide", json=case)
    assert response.status_code == 200
    data = response.json()
    assert data["case_id"] == case["case_id"]
    assert data["decision"] in ("repair", "replace", "escalate")
    assert 0 <= data["confidence"] <= 1
    assert isinstance(data["reason"], str)
