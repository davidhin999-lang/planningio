from flask import Blueprint
from auth.middleware import require_auth  # noqa — imported for patching in tests
billing_bp = Blueprint("billing", __name__, url_prefix="/billing")
