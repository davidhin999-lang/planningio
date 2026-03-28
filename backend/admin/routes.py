from flask import Blueprint
from auth.middleware import require_auth  # noqa — imported for patching in tests
admin_bp = Blueprint("admin", __name__, url_prefix="/admin")
