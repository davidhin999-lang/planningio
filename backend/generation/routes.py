import sys
from flask import Blueprint, request, jsonify, g
from auth.middleware import require_auth  # noqa: F401 — patched in tests via sys.modules
from db import get_session_factory
from billing.usage import check_usage

generation_bp = Blueprint("generation", __name__)


def _auth():
    """Return require_auth from this module (supports test patching)."""
    return sys.modules[__name__].require_auth


@generation_bp.route("/generate", methods=["POST"])
def generate():
    return _auth()(_generate)()


def _generate():
    data = request.get_json(silent=True) or {}
    subject = data.get("subject")
    grade_level = data.get("grade_level")
    topic = data.get("topic")
    objective = data.get("objective")

    if not all([subject, grade_level, topic, objective]):
        return jsonify({"error": "missing_fields", "required": ["subject", "grade_level", "topic", "objective"]}), 400

    Session = get_session_factory()
    with Session() as session:
        allowed, used = check_usage(g.user_id, session)
        if not allowed:
            return jsonify({"error": "limit_reached", "used": used, "limit": 5}), 403

        from generation.pipeline import run_pipeline
        planeacion = run_pipeline(
            user_id=g.user_id,
            subject=subject,
            grade_level=grade_level,
            topic=topic,
            objective=objective,
            session=session,
        )

        return jsonify({
            "id": planeacion.id,
            "title": planeacion.title,
            "content": planeacion.content,
        })
