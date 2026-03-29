from generation.prompt_builder import build_prompt


def test_build_prompt_includes_all_inputs():
    chunks = ["Aprendizaje A", "Aprendizaje B"]
    prompt = build_prompt(
        chunks=chunks,
        subject="Matemáticas",
        grade_level="primaria_3",
        topic="Fracciones",
        objective="Identificar fracciones equivalentes",
    )
    assert "Matemáticas" in prompt
    assert "primaria_3" in prompt
    assert "Fracciones" in prompt
    assert "Identificar fracciones equivalentes" in prompt
    assert "Aprendizaje A" in prompt
    assert "Aprendizaje B" in prompt


def test_build_prompt_requests_json_output():
    prompt = build_prompt([], "Español", "secundaria_1", "Tema", "Objetivo")
    assert "JSON" in prompt or "json" in prompt


def test_build_prompt_handles_empty_chunks():
    prompt = build_prompt([], "Ciencias", "primaria_6", "Ecosistemas", "Identificar ecosistemas")
    assert "Ciencias" in prompt
    assert isinstance(prompt, str)
    assert len(prompt) > 100
