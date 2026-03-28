from functools import wraps
from flask import jsonify, g

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        return jsonify({"error": "not_implemented"}), 501
    return decorated
