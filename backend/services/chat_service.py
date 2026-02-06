from google import genai
from google.genai.errors import ClientError
from pathlib import Path

from config import RESUME_URL
from rag.retriever import retrieve_context

client = genai.Client()
# MODEL_NAME = "models/gemini-flash-lite-latest"
MODEL_NAME = "models/gemini-flash-latest"

BASE_DIR = Path(__file__).resolve().parent.parent
SYSTEM_PROMPT = (BASE_DIR / "prompts" / "system_prompt.txt").read_text(
    encoding="utf-8"
)

def handle_chat(user_message: str):
    try:
        context = retrieve_context(user_message)

        if not context.strip():
            context = "No relevant information found."

        prompt = f"""
{SYSTEM_PROMPT}

Context (authoritative information about Pridhu):
{context}

User question:
{user_message}
"""

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt
        )

        reply = response.text


        asked_for_resume = any(
            kw in user_message.lower()
            for kw in ["resume", "cv", "download"]
        )

        if asked_for_resume and "[RESUME_DOWNLOAD]" in reply:
            reply = reply.replace("[RESUME_DOWNLOAD]", RESUME_URL)
            resume_url = RESUME_URL
        else:
            reply = reply.replace("[RESUME_DOWNLOAD]", "")
            resume_url = None

        return {
            "reply": reply.strip(),
            "resume_url": resume_url
        }

    except ClientError as e:
        if "RESOURCE_EXHAUSTED" in str(e):
            return {
                "reply": "I'm getting too many requests right now. Please try again in a few seconds.",
                "resume_url": None
            }
        raise e
