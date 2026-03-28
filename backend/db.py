from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase


class Base(DeclarativeBase):
    pass


_engine = None
SessionLocal = None


def get_engine(url: str = None):
    global _engine
    if _engine is None:
        from config import Config
        _engine = create_engine(url or Config.DATABASE_URL, echo=False)
    return _engine


def get_session_factory(engine=None):
    global SessionLocal
    if SessionLocal is None:
        SessionLocal = sessionmaker(bind=engine or get_engine(), autoflush=False)
    return SessionLocal


def init_db(engine=None):
    # Import all models so they register with Base.metadata
    import models.models  # noqa — side effect: registers all models
    target = engine or get_engine()
    Base.metadata.create_all(bind=target)


def get_db():
    factory = get_session_factory()
    session = factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
