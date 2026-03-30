import json
from datetime import datetime, timezone, timedelta
from models.models import User, Subscription, Planeacion


def _seed(db_session):
    user = User(id="test-user-id", email="teacher@test.com")
    db_session.add(user)
    sub = Subscription(user_id="test-user-id", plan="free", status="active",
                       current_period_end=datetime.now(timezone.utc) + timedelta(days=30))
    db_session.add(sub)
    p1 = Planeacion(user_id="test-user-id", title="Plan 1", subject="Matemáticas",
                    grade_level="primaria_3", topic="Fracciones",
                    objective="Obj 1", content={"proposito": "p1"})
    p2 = Planeacion(user_id="test-user-id", title="Plan 2", subject="Español",
                    grade_level="primaria_1", topic="Lectura",
                    objective="Obj 2", content={"proposito": "p2"})
    db_session.add_all([p1, p2])
    db_session.commit()
    return p1, p2


def test_list_planeaciones(client, db_session):
    p1, p2 = _seed(db_session)
    resp = client.get("/planeaciones")
    assert resp.status_code == 200
    data = resp.get_json()
    assert len(data) == 2


def test_list_excludes_deleted(client, db_session):
    p1, p2 = _seed(db_session)
    p1.is_deleted = True
    db_session.commit()
    resp = client.get("/planeaciones")
    assert resp.status_code == 200
    assert len(resp.get_json()) == 1


def test_get_planeacion(client, db_session):
    p1, _ = _seed(db_session)
    resp = client.get(f"/planeaciones/{p1.id}")
    assert resp.status_code == 200
    assert resp.get_json()["title"] == "Plan 1"


def test_get_planeacion_404(client, db_session):
    _seed(db_session)
    resp = client.get("/planeaciones/99999")
    assert resp.status_code == 404


def test_delete_planeacion(client, db_session):
    p1, _ = _seed(db_session)
    resp = client.delete(f"/planeaciones/{p1.id}")
    assert resp.status_code == 200
    db_session.refresh(p1)
    assert p1.is_deleted is True


def test_delete_other_users_planeacion(client, db_session):
    other = User(id="other-user", email="other@test.com")
    db_session.add(other)
    p = Planeacion(user_id="other-user", title="Other", subject="S",
                   grade_level="primaria_1", topic="T", objective="O",
                   content={})
    db_session.add(p)
    db_session.commit()
    resp = client.delete(f"/planeaciones/{p.id}")
    assert resp.status_code == 404
