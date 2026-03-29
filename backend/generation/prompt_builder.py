SYSTEM_PROMPT = """Eres un experto en pedagogía mexicana y en el sistema educativo SEP.
Tu tarea es generar planeaciones didácticas completas, estructuradas y listas para entregar,
siguiendo el formato oficial SEP (NEM 2022 / Plan 2011 / Plan 2017 según el nivel).

INSTRUCCIONES:
- Responde ÚNICAMENTE con un objeto JSON válido, sin texto adicional.
- El JSON debe tener exactamente estas claves:
  proposito, inicio, desarrollo, cierre, materiales, evaluacion, competencias, aprendizajes_esperados
- inicio, desarrollo y cierre son objetos con: duracion (string, ej "15 min") y actividades (lista de strings)
- materiales, competencias, aprendizajes_esperados son listas de strings
- proposito y evaluacion son strings
- Usa español mexicano formal.
- Las actividades deben ser concretas, secuenciadas y apropiadas para el nivel.
"""


def build_prompt(
    chunks: list[str],
    subject: str,
    grade_level: str,
    topic: str,
    objective: str,
) -> str:
    context_block = ""
    if chunks:
        context_block = "\n\nAPRENDIZAJES ESPERADOS DEL CURRÍCULO SEP (usa estos como referencia):\n"
        for i, chunk in enumerate(chunks, 1):
            context_block += f"{i}. {chunk}\n"

    user_block = f"""
DATOS DE LA PLANEACIÓN:
- Materia: {subject}
- Nivel/Grado: {grade_level}
- Tema: {topic}
- Objetivo de aprendizaje: {objective}
{context_block}
Genera la planeación didáctica completa en formato JSON.
"""
    return SYSTEM_PROMPT + user_block
