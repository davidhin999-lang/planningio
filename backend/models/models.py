from sqlalchemy import Column, String, Integer, Boolean, Text, DateTime, ForeignKey
from datetime import datetime, timezone
from db import Base


class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True)
    email = Column(String, nullable=False, unique=True)
    display_name = Column(String)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class School(Base):
    __tablename__ = "schools"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    admin_id = Column(String, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class Subscription(Base):
    __tablename__ = "subscriptions"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, ForeignKey("users.id"))
    stripe_customer_id = Column(String, unique=True)
    stripe_sub_id = Column(String, unique=True)
    plan = Column(String, nullable=False, default="free")
    status = Column(String, nullable=False, default="active")
    current_period_end = Column(DateTime(timezone=True))
    school_id = Column(Integer, ForeignKey("schools.id"), nullable=True)


class Planeacion(Base):
    __tablename__ = "planeaciones"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, ForeignKey("users.id"))
    title = Column(String)
    subject = Column(String, nullable=False)
    grade_level = Column(String, nullable=False)
    topic = Column(String, nullable=False)
    objective = Column(String, nullable=False)
    content = Column(Text, nullable=False)  # JSON string (SQLite compatible)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    is_deleted = Column(Boolean, default=False)


class UsageLog(Base):
    __tablename__ = "usage_log"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, ForeignKey("users.id"))
    action = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class CurriculumChunk(Base):
    __tablename__ = "curriculum_chunks"
    id = Column(Integer, primary_key=True, autoincrement=True)
    grade_level = Column(String, nullable=False)
    subject = Column(String, nullable=False)
    source = Column(String, nullable=False)
    chunk_text = Column(Text, nullable=False)
    # embedding column omitted for SQLite test compatibility (pgvector is PostgreSQL-only)
    metadata_ = Column("metadata", Text)  # JSON string
