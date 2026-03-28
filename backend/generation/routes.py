from flask import Blueprint
from auth.middleware import require_auth  # noqa — imported for patching in tests
generation_bp = Blueprint("generation", __name__)
