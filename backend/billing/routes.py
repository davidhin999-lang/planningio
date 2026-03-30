import sys
import stripe
from flask import Blueprint, request, jsonify, g
from auth.middleware import require_auth  # noqa: F401 — patched in tests via sys.modules
from db import get_session_factory
from models.models import Subscription
from datetime import datetime, timezone

billing_bp = Blueprint("billing", __name__, url_prefix="/billing")


def _auth():
    """Return require_auth from this module (supports test patching)."""
    return sys.modules[__name__].require_auth


def _get_or_create_customer(user_id: str, session) -> str:
    sub = session.query(Subscription).filter_by(user_id=user_id).first()
    if sub and sub.stripe_customer_id:
        return sub.stripe_customer_id
    customer = stripe.Customer.create(metadata={"user_id": user_id})
    if sub:
        sub.stripe_customer_id = customer.id
        session.commit()
    return customer.id


@billing_bp.route("/checkout", methods=["POST"])
def checkout():
    return _auth()(_checkout)()


def _checkout():
    data = request.get_json(silent=True) or {}
    plan = data.get("plan", "pro")
    from config import Config
    price_id = Config.STRIPE_PRICE_PRO if plan == "pro" else Config.STRIPE_PRICE_ESCUELA

    stripe.api_key = Config.STRIPE_SECRET_KEY
    Session = get_session_factory()
    with Session() as session:
        customer_id = _get_or_create_customer(g.user_id, session)

    session_obj = stripe.checkout.Session.create(
        customer=customer_id,
        payment_method_types=["card", "oxxo"],
        line_items=[{"price": price_id, "quantity": 1}],
        mode="subscription",
        success_url=f"{Config.FRONTEND_URL}/dashboard?upgraded=1",
        cancel_url=f"{Config.FRONTEND_URL}/billing",
    )
    return jsonify({"checkout_url": session_obj.url})


@billing_bp.route("/portal", methods=["POST"])
def portal():
    return _auth()(_portal)()


def _portal():
    from config import Config
    stripe.api_key = Config.STRIPE_SECRET_KEY
    Session = get_session_factory()
    with Session() as session:
        customer_id = _get_or_create_customer(g.user_id, session)

    session_obj = stripe.billing_portal.Session.create(
        customer=customer_id,
        return_url=f"{Config.FRONTEND_URL}/billing",
    )
    return jsonify({"portal_url": session_obj.url})


@billing_bp.route("/webhook", methods=["POST"])
def webhook():
    payload = request.get_data()
    sig = request.headers.get("Stripe-Signature", "")
    from config import Config
    stripe.api_key = Config.STRIPE_SECRET_KEY

    try:
        event = stripe.Webhook.construct_event(payload, sig, Config.STRIPE_WEBHOOK_SECRET)
    except Exception:
        return jsonify({"error": "invalid_signature"}), 400

    obj = event.data.object
    Session = get_session_factory()
    with Session() as session:
        if event.type == "checkout.session.completed":
            customer_id = obj.get("customer") if isinstance(obj, dict) else obj.customer
            stripe_sub_id = obj.get("subscription") if isinstance(obj, dict) else obj.subscription
            sub = session.query(Subscription).filter_by(stripe_customer_id=customer_id).first()
            if sub:
                sub.stripe_sub_id = stripe_sub_id
                sub.status = "active"
                session.commit()

        elif event.type == "invoice.payment_succeeded":
            customer_id = obj.get("customer") if isinstance(obj, dict) else obj.customer
            period_end = obj.get("lines", {}).get("data", [{}])[0].get("period", {}).get("end") if isinstance(obj, dict) else None
            sub = session.query(Subscription).filter_by(stripe_customer_id=customer_id).first()
            if sub and period_end:
                sub.current_period_end = datetime.fromtimestamp(period_end, tz=timezone.utc)
                sub.status = "active"
                session.commit()

        elif event.type == "customer.subscription.updated":
            customer_id = obj.get("customer") if isinstance(obj, dict) else obj.customer
            status = obj.get("status") if isinstance(obj, dict) else obj.status
            sub = session.query(Subscription).filter_by(stripe_customer_id=customer_id).first()
            if sub:
                sub.status = status
                session.commit()

        elif event.type == "customer.subscription.deleted":
            customer_id = obj.get("customer") if isinstance(obj, dict) else obj.customer
            sub = session.query(Subscription).filter_by(stripe_customer_id=customer_id).first()
            if sub:
                sub.plan = "free"
                sub.status = "canceled"
                session.commit()

    return jsonify({"ok": True})
