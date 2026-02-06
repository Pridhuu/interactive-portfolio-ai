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

app.include_router(router)

@app.get("/health")
def health():
    return {"status": "ok"}
