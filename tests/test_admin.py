from datetime import datetime, timezone, timedelta
from models.models import User, Subscription, School


def _seed_school_admin(db_session):
    admin = User(id="test-user-id", email="admin@school.com")
    db_session.add(admin)
    school = School(name="Escuela Test", admin_id="test-user-id")
    db_session.add(school)
    db_session.flush()
    sub = Subscription(
        user_id="test-user-id",
        plan="escuela",
        status="active",
        school_id=school.id,
        current_period_end=datetime.now(timezone.utc) + timedelta(days=30),
    )
    db_session.add(sub)
    db_session.commit()
    return school


def test_list_school_users(client, db_session):
    school = _seed_school_admin(db_session)
    teacher = User(id="teacher-1", email="teacher1@school.com", display_name="Teacher One")
    db_session.add(teacher)
    teacher_sub = Subscription(
        user_id="teacher-1", plan="escuela", status="active",
        school_id=school.id,
        current_period_end=datetime.now(timezone.utc) + timedelta(days=30),
    )
    db_session.add(teacher_sub)
    db_session.commit()

    resp = client.get("/admin/users")
    assert resp.status_code == 200
    users = resp.get_json()
    assert len(users) == 2  # admin + teacher


def test_list_school_users_403_if_not_escuela(client, db_session):
    user = User(id="test-user-id", email="teacher@test.com")
    db_session.add(user)
    sub = Subscription(user_id="test-user-id", plan="free", status="active",
                       current_period_end=datetime.now(timezone.utc) + timedelta(days=30))
    db_session.add(sub)
    db_session.commit()
    resp = client.get("/admin/users")
    assert resp.status_code == 403


def test_invite_adds_member(client, db_session):
    school = _seed_school_admin(db_session)
    new_user = User(id="new-teacher", email="newteacher@school.com")
    db_session.add(new_user)
    db_session.commit()

    resp = client.post("/admin/invite", json={"email": "newteacher@school.com"})
    assert resp.status_code == 200
    invited_sub = db_session.query(Subscription).filter_by(user_id="new-teacher").first()
    assert invited_sub is not None
    assert invited_sub.school_id == school.id
    assert invited_sub.plan == "escuela"


def test_invite_rejects_at_seat_cap(client, db_session):
    school = _seed_school_admin(db_session)
    for i in range(19):  # admin already is 1 seat
        u = User(id=f"teacher-{i}", email=f"t{i}@school.com")
        db_session.add(u)
        s = Subscription(user_id=f"teacher-{i}", plan="escuela", status="active",
                         school_id=school.id,
                         current_period_end=datetime.now(timezone.utc) + timedelta(days=30))
        db_session.add(s)
    db_session.commit()

    extra = User(id="extra", email="extra@school.com")
    db_session.add(extra)
    db_session.commit()

    resp = client.post("/admin/invite", json={"email": "extra@school.com"})
    assert resp.status_code == 403
    assert resp.get_json()["error"] == "seat_cap_reached"
