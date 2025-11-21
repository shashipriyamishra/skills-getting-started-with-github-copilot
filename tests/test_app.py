import copy

import pytest
from fastapi.testclient import TestClient

from src import app as app_module


client = TestClient(app_module.app)


@pytest.fixture(autouse=True)
def reset_activities():
    # Keep activities isolated between tests
    original = copy.deepcopy(app_module.activities)
    yield
    app_module.activities.clear()
    app_module.activities.update(original)


def test_signup_and_unregister_flow():
    activity = "Chess Club"
    email = "testuser@example.com"

    # ensure clean start
    assert email not in app_module.activities[activity]["participants"]

    # signup
    resp = client.post(f"/activities/{activity}/signup?email={email}")
    assert resp.status_code == 200
    data = resp.json()
    assert "Signed up" in data["message"]
    assert email in app_module.activities[activity]["participants"]

    # unregister
    resp = client.delete(f"/activities/{activity}/participants?email={email}")
    assert resp.status_code == 200
    data = resp.json()
    assert "Unregistered" in data["message"]
    assert email not in app_module.activities[activity]["participants"]


def test_unregister_nonexistent_returns_404():
    activity = "Chess Club"
    email = "doesnotexist@example.com"

    # ensure it's not present
    if email in app_module.activities[activity]["participants"]:
        app_module.activities[activity]["participants"].remove(email)

    resp = client.delete(f"/activities/{activity}/participants?email={email}")
    assert resp.status_code == 404


def test_signup_existing_returns_400():
    activity = "Chess Club"
    # pick an existing participant
    email = app_module.activities[activity]["participants"][0]

    resp = client.post(f"/activities/{activity}/signup?email={email}")
    assert resp.status_code == 400
