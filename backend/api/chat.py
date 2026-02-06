from fastapi import APIRouter
from pydantic import BaseModel
from services.chat_service import handle_chat

router = APIRouter()

class ChatRequest(BaseModel):
    message: str

@router.post("/chat")
def chat(req: ChatRequest):
    return handle_chat(req.message)
