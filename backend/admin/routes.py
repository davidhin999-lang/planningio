import sys
from flask import Blueprint, request, jsonify, g
from auth.middleware import require_auth  # noqa: F401 — patched in tests via sys.modules
from db import get_session_factory
from models.models import User, Subscription, School

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

SEAT_CAP = 20


def _auth():
    """Return require_auth from this module (supports test patching)."""
    return sys.modules[__name__].require_auth


def _get_school(user_id: str, session):
    """Return the school if the user is an escuela admin, else None."""
    sub = session.query(Subscription).filter_by(user_id=user_id).first()
    if not sub or sub.plan != "escuela" or not sub.school_id:
        return None
    school = session.get(School, sub.school_id)
    if school is None or school.admin_id != user_id:
        return None
    return school


@admin_bp.route("/users", methods=["GET"])
def list_users():
    return _auth()(_list_users)()


def _list_users():
    Session = get_session_factory()
    with Session() as session:
        school = _get_school(g.user_id, session)
        if school is None:
            return jsonify({"error": "forbidden"}), 403

        members = session.query(Subscription).filter_by(school_id=school.id).all()
        result = []
        for m in members:
            user = session.get(User, m.user_id)
            if user:
                result.append({
                    "id": user.id,
                    "email": user.email,
                    "display_name": user.display_name,
                    "status": m.status,
                })
        return jsonify(result)


@admin_bp.route("/invite", methods=["POST"])
def invite():
    return _auth()(_invite)()


def _invite():
    data = request.get_json(silent=True) or {}
    email = data.get("email")
    if not email:
        return jsonify({"error": "missing_email"}), 400

    Session = get_session_factory()
    with Session() as session:
        school = _get_school(g.user_id, session)
        if school is None:
            return jsonify({"error": "forbidden"}), 403

        seat_count = session.query(Subscription).filter_by(school_id=school.id).count()
        if seat_count >= SEAT_CAP:
            return jsonify({"error": "seat_cap_reached", "cap": SEAT_CAP}), 403

        user = session.query(User).filter_by(email=email).first()
        if user is None:
            return jsonify({"error": "user_not_found"}), 404

        existing_sub = session.query(Subscription).filter_by(user_id=user.id).first()
        if existing_sub:
            existing_sub.plan = "escuela"
            existing_sub.school_id = school.id
            existing_sub.status = "active"
        else:
            new_sub = Subscription(
                user_id=user.id,
                plan="escuela",
                status="active",
                school_id=school.id,
            )
            session.add(new_sub)

        session.commit()
        return jsonify({"ok": True, "invited": email})
