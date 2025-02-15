import pytest
from fastapi.testclient import TestClient
from services.api.main import app
from services.api.models import GoalRequest

client = TestClient(app)

@pytest.fixture
def valid_goal_request():
    return {"goal": "Test Goal", "priority": "high"}

def test_add_goal(valid_goal_request):
    response = client.post("/goals/", json=valid_goal_request)
    assert response.status_code == 200
    assert response.json()["message"] == "Goal added successfully."
    assert "goal_id" in response.json()

def test_add_goal_invalid():
    # Test missing goal
    response = client.post("/goals/", json={})
    assert response.status_code == 422

    # Test invalid priority
    response = client.post("/goals/", json={"goal": "Test", "priority": "invalid"})
    assert response.status_code == 422

def test_get_goals():
    response = client.get("/goals/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
