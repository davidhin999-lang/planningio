from unittest.mock import MagicMock, patch


def test_retrieve_chunks_returns_texts(db_session):
    from generation.retriever import retrieve_chunks
    # Mock the raw SQL execution to return 2 rows
    mock_row1 = MagicMock()
    mock_row1.chunk_text = "Los alumnos identificarán fracciones"
    mock_row1.metadata_ = {"aprendizaje": "Fracciones equivalentes"}
    mock_row2 = MagicMock()
    mock_row2.chunk_text = "Usar materiales concretos para fracciones"
    mock_row2.metadata_ = None

    with patch.object(db_session, "execute") as mock_exec:
        mock_exec.return_value.fetchall.return_value = [mock_row1, mock_row2]
        results = retrieve_chunks([0.1] * 768, "primaria_3", "Matemáticas", db_session)

    assert len(results) == 2
    assert results[0] == "Los alumnos identificarán fracciones"
    assert results[1] == "Usar materiales concretos para fracciones"
