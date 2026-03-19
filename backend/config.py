import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Public URL where the resume PDF is served from (set in production env)
RESUME_URL = os.getenv("RESUME_URL", "http://127.0.0.1:8000/static/Resume.pdf")

# ChromaDB persistence directory (use /tmp on Render since disk is ephemeral)
CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", str(BASE_DIR / "chroma"))
