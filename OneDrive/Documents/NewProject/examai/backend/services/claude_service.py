import google.generativeai as genai
import base64
import json
import re
import os

# Validate API key is set
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY environment variable is not set")

# Initialize Gemini API
genai.configure(api_key=api_key)

SYSTEM_PROMPT = """Eres un asistente de corrección de exámenes para profesores de educación básica y media.
Tu trabajo es revisar la imagen de un examen escrito por un alumno y calificarlo con base en la rúbrica proporcionada.

Reglas:
- Sé justo pero estricto. Si la respuesta está incompleta, descuenta puntos parcialmente.
- Escribe los comentarios en español, en tono profesional y constructivo.
- Si no puedes leer claramente una respuesta, indícalo con "ilegible" y asigna 0 puntos.
- No inventes respuestas que no estén en la imagen.

Responde ÚNICAMENTE con un JSON con esta estructura exacta, sin backticks ni texto adicional:
{
  "questions": [
    {
      "id": "1a",
      "student_answer": "lo que escribió el alumno",
      "points_earned": 8,
      "max_points": 10,
      "comment": "comentario constructivo breve"
    }
  ],
  "total_score": 38,
  "max_score": 50,
  "percentage": 76,
  "overall_comment": "comentario general sobre el desempeño del alumno en 2-3 oraciones",
  "grade_letter": "B"
}"""


def grade_exam(image_bytes: bytes, media_type: str, rubric: list, language: str = "es") -> dict:
    """Send exam image + rubric to Gemini for grading. Returns parsed result dict."""
    image_b64 = base64.standard_b64encode(image_bytes).decode("utf-8")
    rubric_text = json.dumps(rubric, ensure_ascii=False, indent=2)

    # Prepare rubric and prompt text
    user_prompt = (
        f"Aquí está la rúbrica para calificar este examen:\n{rubric_text}\n\n"
        "Por favor, revisa la imagen del examen y califica cada pregunta según la rúbrica. "
        "Responde únicamente con el JSON solicitado."
    )

    # Map media_type to Gemini format
    mime_type = _get_gemini_mime_type(media_type)

    # Create model and send request with image + text
    model = genai.GenerativeModel(
        model_name="gemini-2.0-flash",
        system_instruction=SYSTEM_PROMPT,
    )

    # Build message content: image + text
    content = [
        {
            "mime_type": mime_type,
            "data": image_b64,
        },
        {"text": user_prompt}
    ]

    try:
        response = model.generate_content(content)
    except Exception as exc:
        raise ValueError(f"Gemini API error: {exc}") from exc

    raw_text = response.text

    return _parse_json_response(raw_text)


def _get_gemini_mime_type(anthropic_media_type: str) -> str:
    """Convert Anthropic media type to Gemini format.

    Anthropic uses: "image/jpeg", "image/png"
    Gemini expects: "image/jpeg", "image/png" (same format, just ensuring consistency)
    """
    # Anthropic and Gemini use the same MIME types
    return anthropic_media_type


def _parse_json_response(text: str) -> dict:
    """Safely parse JSON from Gemini's response, handling common formatting issues."""
    text = text.strip()

    # Strip markdown code fences if present
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    text = text.strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Try to extract a JSON object from the text
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass
        raise ValueError(
            f"Could not parse a valid JSON object from Gemini's response. Raw output:\n{text[:500]}"
        )
