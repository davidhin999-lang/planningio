import pytest
from datetime import datetime, timezone, timedelta
from billing.usage import check_usage
from models.models import User, Subscription, UsageLog


def _make_sub(session, user_id, plan):
    from datetime import datetime, timezone, timedelta
    user = User(id=user_id, email=f"{user_id}@test.com")
    session.add(user)
    sub = Subscription(
        user_id=user_id,
        plan=plan,
        status="active",
        current_period_end=datetime.now(timezone.utc) + timedelta(days=30),
    )
    session.add(sub)
    session.commit()
    return sub


def test_free_tier_allows_under_limit(db_session):
    _make_sub(db_session, "u1", "free")
    # 4 logs this month
    for _ in range(4):
        db_session.add(UsageLog(user_id="u1", action="generate"))
    db_session.commit()
    allowed, used = check_usage("u1", db_session)
    assert allowed is True
    assert used == 4


def test_free_tier_blocks_at_limit(db_session):
    _make_sub(db_session, "u2", "free")
    for _ in range(5):
        db_session.add(UsageLog(user_id="u2", action="generate"))
    db_session.commit()
    allowed, used = check_usage("u2", db_session)
    assert allowed is False
    assert used == 5


def test_pro_tier_always_allowed(db_session):
    _make_sub(db_session, "u3", "pro")
    for _ in range(100):
        db_session.add(UsageLog(user_id="u3", action="generate"))
    db_session.commit()
    allowed, used = check_usage("u3", db_session)
    assert allowed is True


def test_escuela_tier_always_allowed(db_session):
    _make_sub(db_session, "u4", "escuela")
    allowed, used = check_usage("u4", db_session)
    assert allowed is True
