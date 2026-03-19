from dotenv import load_dotenv
load_dotenv()

import asyncio
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from api.chat import router

app = FastAPI(title="Interactive Portfolio AI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files (Resume PDF, etc.)
STATIC_DIR = Path(__file__).resolve().parent / "static"
STATIC_DIR.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

app.include_router(router)


def _background_startup():
    """
    Heavy startup work: PDF parsing + vector DB ingestion.
    Runs in a thread pool so the port binds immediately and
    Render doesn't time out waiting for the server to be ready.
    """
    try:
        from services.resume_parser import ensure_resume_json_exists
        ensure_resume_json_exists()
    except Exception as e:
        print(f"⚠️  Resume parser error (non-fatal): {e}")

    try:
        from rag.ingest import ingest_if_needed
        ingest_if_needed()
    except Exception as e:
        print(f"⚠️  Ingest error (non-fatal): {e}")


@app.on_event("startup")
async def startup_event():
    """
    Kick off heavy work in a background thread.
    The server binds the port and accepts requests immediately.
    The first few requests may have empty context (handled gracefully).
    """
    loop = asyncio.get_event_loop()
    loop.run_in_executor(ThreadPoolExecutor(max_workers=1), _background_startup)
    print("✅ Server started. Background ingestion running...")


@app.get("/health")
def health():
    return {"status": "ok"}
