import pytest
import json
from models.models import User, Subscription


def test_sync_creates_user_and_subscription(client, db_session):
    resp = client.post("/auth/sync", json={"email": "teacher@test.com", "display_name": "Ana"})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["user"]["id"] == "test-user-id"
    assert data["subscription"]["plan"] == "free"
    assert data["subscription"]["status"] == "active"

    user = db_session.get(User, "test-user-id")
    assert user is not None
    assert user.email == "teacher@test.com"


def test_sync_is_idempotent(client, db_session):
    client.post("/auth/sync", json={"email": "teacher@test.com", "display_name": "Ana"})
    resp = client.post("/auth/sync", json={"email": "teacher@test.com", "display_name": "Ana"})
    assert resp.status_code == 200
    count = db_session.query(User).filter_by(id="test-user-id").count()
    assert count == 1


def test_me_returns_user_and_subscription(client, db_session, seeded_user):
    resp = client.get("/auth/me")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["user"]["id"] == "test-user-id"
    assert data["subscription"]["plan"] == "free"


def test_me_returns_404_if_no_user(client, db_session):
    resp = client.get("/auth/me")
    assert resp.status_code == 404
