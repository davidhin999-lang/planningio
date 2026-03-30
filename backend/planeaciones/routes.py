import sys
from flask import Blueprint, jsonify, g
from auth.middleware import require_auth  # noqa: F401 — patched in tests via sys.modules
from db import get_session_factory
from models.models import Planeacion

planeaciones_bp = Blueprint("planeaciones", __name__, url_prefix="/planeaciones")


def _auth():
    """Return require_auth from this module (supports test patching)."""
    return sys.modules[__name__].require_auth


def _plan_dict(p):
    return {
        "id": p.id,
        "title": p.title,
        "subject": p.subject,
        "grade_level": p.grade_level,
        "topic": p.topic,
        "objective": p.objective,
        "content": p.content,
        "created_at": p.created_at.isoformat() if p.created_at else None,
    }


@planeaciones_bp.route("", methods=["GET"])
def list_planeaciones():
    return _auth()(_list_planeaciones)()


def _list_planeaciones():
    Session = get_session_factory()
    with Session() as session:
        plans = session.query(Planeacion).filter_by(
            user_id=g.user_id, is_deleted=False
        ).order_by(Planeacion.created_at.desc()).all()
        return jsonify([_plan_dict(p) for p in plans])


@planeaciones_bp.route("/<int:plan_id>", methods=["GET"])
def get_planeacion(plan_id):
    return _auth()(_get_planeacion)(plan_id)


def _get_planeacion(plan_id):
    Session = get_session_factory()
    with Session() as session:
        p = session.query(Planeacion).filter_by(
            id=plan_id, user_id=g.user_id, is_deleted=False
        ).first()
        if p is None:
            return jsonify({"error": "not_found"}), 404
        return jsonify(_plan_dict(p))


@planeaciones_bp.route("/<int:plan_id>", methods=["DELETE"])
def delete_planeacion(plan_id):
    return _auth()(_delete_planeacion)(plan_id)


def _delete_planeacion(plan_id):
    Session = get_session_factory()
    with Session() as session:
        p = session.query(Planeacion).filter_by(
            id=plan_id, user_id=g.user_id, is_deleted=False
        ).first()
        if p is None:
            return jsonify({"error": "not_found"}), 404
        p.is_deleted = True
        session.commit()
        return jsonify({"ok": True})
