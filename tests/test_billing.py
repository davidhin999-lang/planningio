import json
import hmac
import hashlib
import time
from unittest.mock import patch, MagicMock
from models.models import User, Subscription


def _seed_user(db_session, plan="free"):
    from datetime import datetime, timezone, timedelta
    user = User(id="test-user-id", email="teacher@test.com")
    db_session.add(user)
    sub = Subscription(
        user_id="test-user-id",
        plan=plan,
        status="active",
        stripe_customer_id="cus_test123",
        current_period_end=datetime.now(timezone.utc) + timedelta(days=30),
    )
    db_session.add(sub)
    db_session.commit()
    return sub


def test_checkout_creates_session(client, db_session):
    _seed_user(db_session)
    mock_session = MagicMock()
    mock_session.url = "https://checkout.stripe.com/pay/cs_test"
    with patch("billing.routes.stripe") as mock_stripe:
        mock_stripe.checkout.Session.create.return_value = mock_session
        resp = client.post("/billing/checkout", json={"plan": "pro"})
    assert resp.status_code == 200
    assert "checkout_url" in resp.get_json()


def test_portal_creates_session(client, db_session):
    _seed_user(db_session)
    mock_session = MagicMock()
    mock_session.url = "https://billing.stripe.com/session/test"
    with patch("billing.routes.stripe") as mock_stripe:
        mock_stripe.billing_portal.Session.create.return_value = mock_session
        resp = client.post("/billing/portal")
    assert resp.status_code == 200
    assert "portal_url" in resp.get_json()


def _make_webhook_sig(payload: bytes, secret: str) -> str:
    ts = str(int(time.time()))
    signed = f"{ts}.{payload.decode()}"
    sig = hmac.new(secret.encode(), signed.encode(), hashlib.sha256).hexdigest()
    return f"t={ts},v1={sig}"


def test_webhook_subscription_deleted(client, db_session, app):
    sub = _seed_user(db_session, plan="pro")
    payload = json.dumps({
        "type": "customer.subscription.deleted",
        "data": {"object": {"id": "sub_test", "customer": "cus_test123", "status": "canceled"}},
    }).encode()
    secret = "whsec_test"
    app.config["STRIPE_WEBHOOK_SECRET"] = secret

    mock_event = MagicMock()
    mock_event.type = "customer.subscription.deleted"
    mock_event.data.object = {"id": "sub_test", "customer": "cus_test123", "status": "canceled"}
    with patch("billing.routes.stripe") as mock_stripe:
        mock_stripe.Webhook.construct_event.return_value = mock_event
        resp = client.post(
            "/billing/webhook",
            data=payload,
            content_type="application/json",
            headers={"Stripe-Signature": "t=1,v1=fake"},
        )
    assert resp.status_code == 200
    db_session.refresh(sub)
    assert sub.plan == "free"
    assert sub.status == "canceled"
