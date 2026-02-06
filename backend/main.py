from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from api.chat import router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Interactive Portfolio AI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    from services.data_loader import load_profile_text
    from rag.vectordb import add_documents, reset_db

    print("Ingesting data...")
    reset_db()
    docs, ids, sections = load_profile_text()
    add_documents(docs, ids, sections)
    print("Data ingestion complete.")
