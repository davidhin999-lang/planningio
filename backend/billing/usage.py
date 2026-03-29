from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import func
from models.models import Subscription, UsageLog

FREE_TIER_LIMIT = 5


def check_usage(user_id: str, session: Session) -> tuple[bool, int]:
    """
    Returns (allowed, used_this_month).
    allowed=True means the user can generate another planeación.
    """
    sub = session.query(Subscription).filter_by(user_id=user_id).first()
    if sub is None or sub.plan != "free":
        # Pro and Escuela tiers are unlimited
        count = session.query(func.count(UsageLog.id)).filter(
            UsageLog.user_id == user_id,
            UsageLog.action == "generate",
        ).scalar() or 0
        return True, count

    # Free tier: count this calendar month
    month_start = datetime.now(timezone.utc).replace(
        day=1, hour=0, minute=0, second=0, microsecond=0
    )
    count = session.query(func.count(UsageLog.id)).filter(
        UsageLog.user_id == user_id,
        UsageLog.action == "generate",
        UsageLog.created_at >= month_start,
    ).scalar() or 0

    return count < FREE_TIER_LIMIT, count
