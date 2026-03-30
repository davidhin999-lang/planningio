import json
import google.generativeai as genai
from config import Config
from generation.embedder import embed_text
from generation.retriever import retrieve_chunks
from generation.prompt_builder import build_prompt

genai.configure(api_key=Config.GOOGLE_API_KEY)

GEMINI_MODEL = "gemini-2.0-flash"

RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "proposito": {"type": "string"},
        "inicio": {
            "type": "object",
            "properties": {
                "duracion": {"type": "string"},
                "actividades": {"type": "array", "items": {"type": "string"}},
            },
        },
        "desarrollo": {
            "type": "object",
            "properties": {
                "duracion": {"type": "string"},
                "actividades": {"type": "array", "items": {"type": "string"}},
            },
        },
        "cierre": {
            "type": "object",
            "properties": {
                "duracion": {"type": "string"},
                "actividades": {"type": "array", "items": {"type": "string"}},
            },
        },
        "materiales": {"type": "array", "items": {"type": "string"}},
        "evaluacion": {"type": "string"},
        "competencias": {"type": "array", "items": {"type": "string"}},
        "aprendizajes_esperados": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["proposito", "inicio", "desarrollo", "cierre", "materiales", "evaluacion", "competencias", "aprendizajes_esperados"],
}


def call_gemini(prompt: str) -> dict:
    """Call Gemini 2.0 Flash with structured JSON output."""
    model = genai.GenerativeModel(
        model_name=GEMINI_MODEL,
        generation_config={
            "response_mime_type": "application/json",
            "response_schema": RESPONSE_SCHEMA,
        },
    )
    response = model.generate_content(prompt)
    return json.loads(response.text)


def run_pipeline(
    user_id: str,
    subject: str,
    grade_level: str,
    topic: str,
    objective: str,
    session,
) -> dict:
    """Full RAG + generation pipeline. Returns planeacion content dict."""
    from models.models import Planeacion, UsageLog

    # 1. Embed query
    query = f"{subject} {grade_level} {topic} {objective}"
    embedding = embed_text(query)

    # 2. Retrieve curriculum chunks
    chunks = retrieve_chunks(embedding, grade_level, subject, session)

    # 3. Build prompt
    prompt = build_prompt(chunks, subject, grade_level, topic, objective)

    # 4. Call Gemini
    content = call_gemini(prompt)

    # 5. Store planeacion
    title = f"{subject} {grade_level.replace('_', ' ').title()} - {topic}"
    planeacion = Planeacion(
        user_id=user_id,
        title=title,
        subject=subject,
        grade_level=grade_level,
        topic=topic,
        objective=objective,
        content=content,
    )
    session.add(planeacion)

    # 6. Log usage
    log = UsageLog(user_id=user_id, action="generate")
    session.add(log)

    session.commit()
    session.refresh(planeacion)
    return planeacion
