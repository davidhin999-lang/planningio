from flask import Blueprint
from auth.middleware import require_auth  # noqa — imported for patching in tests
planeaciones_bp = Blueprint("planeaciones", __name__, url_prefix="/planeaciones")
