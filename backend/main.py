from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path

from api.chat import router
from services.resume_parser import ensure_resume_json_exists
from rag.ingest import ingest_if_needed

app = FastAPI(title="Interactive Portfolio AI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files (resume PDF, etc.)
STATIC_DIR = Path(__file__).resolve().parent / "static"
STATIC_DIR.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

app.include_router(router)


@app.on_event("startup")
def startup_event():
    """
    On startup:
    1. If resume.pdf exists but resume_parsed.json doesn't → parse PDF → write JSON.
    2. If vector DB is empty → ingest all JSON docs into ChromaDB.
    """
    ensure_resume_json_exists()
    ingest_if_needed()


@app.get("/health")
def health():
    return {"status": "ok"}
