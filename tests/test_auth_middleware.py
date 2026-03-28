import pytest
from unittest.mock import patch
from flask import Flask, g, jsonify
from auth.middleware import require_auth


def _make_protected_app():
    app = Flask(__name__)

    @app.route("/protected")
    @require_auth
    def protected():
        return jsonify({"user_id": g.user_id})

    return app


def test_missing_authorization_header():
    app = _make_protected_app()
    with app.test_client() as c:
        resp = c.get("/protected")
    assert resp.status_code == 401
    assert resp.get_json()["error"] == "missing_token"


def test_malformed_authorization_header():
    app = _make_protected_app()
    with app.test_client() as c:
        resp = c.get("/protected", headers={"Authorization": "NotBearer abc"})
    assert resp.status_code == 401
    assert resp.get_json()["error"] == "missing_token"


def test_invalid_firebase_token():
    import firebase_admin.auth as fba
    app = _make_protected_app()
    with patch.object(fba, "verify_id_token", side_effect=fba.InvalidIdTokenError("bad")):
        with app.test_client() as c:
            resp = c.get("/protected", headers={"Authorization": "Bearer bad-token"})
    assert resp.status_code == 401
    assert resp.get_json()["error"] == "invalid_token"


def test_valid_firebase_token_injects_user_id():
    import firebase_admin.auth as fba
    app = _make_protected_app()
    with patch.object(fba, "verify_id_token", return_value={"uid": "user-abc"}):
        with app.test_client() as c:
            resp = c.get("/protected", headers={"Authorization": "Bearer valid-token"})
    assert resp.status_code == 200
    assert resp.get_json()["user_id"] == "user-abc"
