import json
from unittest.mock import patch, MagicMock
from models.models import User, Subscription, UsageLog, Planeacion


SAMPLE_CONTENT = {
    "proposito": "El alumno identificará fracciones equivalentes.",
    "inicio": {"duracion": "10 min", "actividades": ["Presentar fracciones con pizza"]},
    "desarrollo": {"duracion": "30 min", "actividades": ["Usar regletas de fracciones"]},
    "cierre": {"duracion": "10 min", "actividades": ["Reflexión grupal"]},
    "materiales": ["Regletas", "Fichas"],
    "evaluacion": "Observación directa y lista de cotejo.",
    "competencias": ["Resolución de problemas"],
    "aprendizajes_esperados": ["Identifica fracciones equivalentes"],
}


def _seed_pro_user(db_session):
    from datetime import datetime, timezone, timedelta
    user = User(id="test-user-id", email="teacher@test.com")
    db_session.add(user)
    sub = Subscription(
        user_id="test-user-id",
        plan="pro",
        status="active",
        current_period_end=datetime.now(timezone.utc) + timedelta(days=30),
    )
    db_session.add(sub)
    db_session.commit()


def test_generate_returns_planeacion(client, db_session):
    _seed_pro_user(db_session)
    with patch("generation.pipeline.embed_text", return_value=[0.1] * 768), \
         patch("generation.pipeline.retrieve_chunks", return_value=[]), \
         patch("generation.pipeline.call_gemini", return_value=SAMPLE_CONTENT):
        resp = client.post("/generate", json={
            "subject": "Matemáticas",
            "grade_level": "primaria_3",
            "topic": "Fracciones",
            "objective": "Identificar fracciones equivalentes",
        })
    assert resp.status_code == 200
    data = resp.get_json()
    assert "id" in data
    assert data["content"]["proposito"] == SAMPLE_CONTENT["proposito"]


def test_generate_logs_usage(client, db_session):
    _seed_pro_user(db_session)
    with patch("generation.pipeline.embed_text", return_value=[0.1] * 768), \
         patch("generation.pipeline.retrieve_chunks", return_value=[]), \
         patch("generation.pipeline.call_gemini", return_value=SAMPLE_CONTENT):
        client.post("/generate", json={
            "subject": "Español",
            "grade_level": "primaria_1",
            "topic": "Lectura",
            "objective": "Leer en voz alta",
        })
    logs = db_session.query(UsageLog).filter_by(user_id="test-user-id", action="generate").all()
    assert len(logs) == 1


def test_generate_blocks_free_user_at_limit(client, db_session):
    from datetime import datetime, timezone, timedelta
    user = User(id="test-user-id", email="teacher@test.com")
    db_session.add(user)
    sub = Subscription(
        user_id="test-user-id",
        plan="free",
        status="active",
        current_period_end=datetime.now(timezone.utc) + timedelta(days=30),
    )
    db_session.add(sub)
    for _ in range(5):
        db_session.add(UsageLog(user_id="test-user-id", action="generate"))
    db_session.commit()
    resp = client.post("/generate", json={
        "subject": "Matemáticas",
        "grade_level": "primaria_3",
        "topic": "Sumas",
        "objective": "Sumar números de dos dígitos",
    })
    assert resp.status_code == 403
    data = resp.get_json()
    assert data["error"] == "limit_reached"
    assert data["limit"] == 5


def test_generate_requires_all_fields(client, db_session):
    _seed_pro_user(db_session)
    resp = client.post("/generate", json={"subject": "Matemáticas"})
    assert resp.status_code == 400
