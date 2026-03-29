from sqlalchemy.orm import Session
from sqlalchemy import text

TOP_K = 5


def retrieve_chunks(
    embedding: list[float],
    grade_level: str,
    subject: str,
    session: Session,
) -> list[str]:
    """
    Vector similarity search with pre-filter on grade_level + subject.
    In production (PostgreSQL + pgvector): uses <=> operator.
    In tests (SQLite): caller should mock session.execute.
    """
    vector_str = "[" + ",".join(str(v) for v in embedding) + "]"
    sql = text("""
        SELECT chunk_text, metadata
        FROM curriculum_chunks
        WHERE grade_level = :grade AND subject = :subject
        ORDER BY embedding <=> CAST(:vec AS vector)
        LIMIT :k
    """)
    rows = session.execute(sql, {
        "grade": grade_level,
        "subject": subject,
        "vec": vector_str,
        "k": TOP_K,
    }).fetchall()
    return [row.chunk_text for row in rows]
