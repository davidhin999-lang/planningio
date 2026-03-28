from functools import wraps
from flask import request, jsonify, g
import firebase_admin.auth as fba


def require_auth(f):
    """Verify Firebase Bearer token → g.user_id."""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "missing_token"}), 401
        id_token = auth_header[len("Bearer "):]
        try:
            decoded = fba.verify_id_token(id_token)
        except Exception:
            return jsonify({"error": "invalid_token"}), 401
        g.user_id = decoded["uid"]
        return f(*args, **kwargs)
    return decorated
