import google.generativeai as genai
from config import Config

genai.configure(api_key=Config.GOOGLE_API_KEY)

EMBEDDING_MODEL = "models/text-embedding-004"


def embed_text(text: str) -> list[float]:
    """Embed text using Google text-embedding-004. Returns 768-dim vector."""
    result = genai.embed_content(model=EMBEDDING_MODEL, content=text)
    return result.embeddings[0].values
