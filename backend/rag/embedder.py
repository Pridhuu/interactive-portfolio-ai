"""
Embedder using Gemini's gemini-embedding-001 model via API.
No model download required — embeddings are fetched as API calls (~100ms each).
Output dimension: 768
"""
from __future__ import annotations
from google import genai

_client: genai.Client | None = None

def _get_client() -> genai.Client:
    global _client
    if _client is None:
        _client = genai.Client()
    return _client

def embed(text: str) -> list[float]:
    """Return a 768-dim embedding vector for the given text."""
    result = _get_client().models.embed_content(
        model="models/gemini-embedding-001",
        contents=text,
    )
    return result.embeddings[0].values
