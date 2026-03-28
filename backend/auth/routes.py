import sys
from flask import Blueprint, request, jsonify, g
from auth.middleware import require_auth
from db import get_session_factory
from models.models import User, Subscription

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


def _sub_dict(sub):
    return {
        "plan": sub.plan,
        "status": sub.status,
        "current_period_end": sub.current_period_end.isoformat() if sub.current_period_end else None,
    }


def _auth():
    """Return the current require_auth from this module (supports test patching)."""
    return sys.modules[__name__].require_auth


@auth_bp.route("/sync", methods=["POST"])
def sync():
    return _auth()(_sync)()


def _sync():
    data = request.get_json(silent=True) or {}
    email = data.get("email", "")
    display_name = data.get("display_name")
    user_id = g.user_id

    Session = get_session_factory()
    with Session() as session:
        user = session.get(User, user_id)
        if user is None:
            user = User(id=user_id, email=email, display_name=display_name)
            session.add(user)
        else:
            if email:
                user.email = email
            if display_name:
                user.display_name = display_name

        sub = session.query(Subscription).filter_by(user_id=user_id).first()
        if sub is None:
            sub = Subscription(user_id=user_id, plan="free", status="active")
            session.add(sub)

        session.commit()
        session.refresh(user)
        session.refresh(sub)

        return jsonify({
            "user": {"id": user.id, "email": user.email, "display_name": user.display_name},
            "subscription": _sub_dict(sub),
        })


@auth_bp.route("/me", methods=["GET"])
def me():
    return _auth()(_me)()


def _me():
    Session = get_session_factory()
    with Session() as session:
        user = session.get(User, g.user_id)
        if user is None:
            return jsonify({"error": "user_not_found"}), 404

        sub = session.query(Subscription).filter_by(user_id=g.user_id).first()
        return jsonify({
            "user": {"id": user.id, "email": user.email, "display_name": user.display_name},
            "subscription": _sub_dict(sub) if sub else {"plan": "free", "status": "active", "current_period_end": None},
        })
