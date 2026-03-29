from unittest.mock import patch, MagicMock


def test_embed_text_returns_768_floats():
    from generation.embedder import embed_text
    mock_result = MagicMock()
    mock_result.embeddings = [MagicMock(values=[0.1] * 768)]
    with patch("generation.embedder.genai") as mock_genai:
        mock_genai.embed_content.return_value = mock_result
        result = embed_text("Matemáticas primaria_3 Fracciones")
    assert len(result) == 768
    assert result[0] == 0.1


def test_embed_text_calls_correct_model():
    from generation.embedder import embed_text
    mock_result = MagicMock()
    mock_result.embeddings = [MagicMock(values=[0.0] * 768)]
    with patch("generation.embedder.genai") as mock_genai:
        mock_genai.embed_content.return_value = mock_result
        embed_text("test query")
        mock_genai.embed_content.assert_called_once_with(
            model="models/text-embedding-004",
            content="test query",
        )
