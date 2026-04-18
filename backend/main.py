from dotenv import load_dotenv
load_dotenv()

from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from api.chat import router
from services.resume_parser import ensure_resume_json_exists
from rag.ingest import ingest_if_needed, force_reingest

app = FastAPI(title="Interactive Portfolio AI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files (Resume PDF)
STATIC_DIR = Path(__file__).resolve().parent / "static"
STATIC_DIR.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

app.include_router(router)


@app.on_event("startup")
def startup():
    """On every deployment/restart: detect PDF changes and sync ChromaDB."""
    pdf_changed = ensure_resume_json_exists()
    if pdf_changed:
        # Resume.pdf was updated — wipe + re-ingest ChromaDB with fresh data
        force_reingest()
    else:
        # Normal startup — ingest only if ChromaDB is empty (first deploy)
        ingest_if_needed()


@app.get("/health")
def health():
    return {"status": "ok"}
