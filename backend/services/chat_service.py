import json
from google import genai
from google.genai.errors import ClientError
from pathlib import Path

from config import RESUME_URL
from rag.retriever import retrieve_context

client = genai.Client()
MODEL_NAME = "models/gemini-flash-latest"

BASE_DIR = Path(__file__).resolve().parent.parent
PROMPT_FILE = BASE_DIR / "prompts" / "system_prompt.txt"

# Cache prompt + mtime to avoid disk read every request
_prompt_cache: str = ""
_prompt_mtime: float = 0.0

def get_system_prompt() -> str:
    """Return cached prompt; re-read from disk only if the file changed."""
    global _prompt_cache, _prompt_mtime
    mtime = PROMPT_FILE.stat().st_mtime
    if mtime != _prompt_mtime:
        _prompt_cache = PROMPT_FILE.read_text(encoding="utf-8")
        _prompt_mtime = mtime
    return _prompt_cache


def _build_prompt(user_message: str) -> str:
    context = retrieve_context(user_message, k=3)
    if not context.strip():
        context = "No relevant information found."
    return f"""{get_system_prompt()}

Context (authoritative information about Pridhu):
{context}

User question:
{user_message}
"""


def stream_chat(user_message: str):
    """
    Generator that yields SSE-formatted chunks.

    Each chunk: data: {{"token": "..."}}\n\n
    Final chunk: data: {{"done": true, "resume_url": "..."|null}}\n\n
    Error chunk: data: {{"error": "..."}}\n\n
    """
    try:
        prompt = _build_prompt(user_message)
        asked_for_resume = any(
            kw in user_message.lower()
            for kw in ["resume", "cv", "download"]
        )

        full_reply = ""

        for chunk in client.models.generate_content_stream(
            model=MODEL_NAME,
            contents=prompt,
        ):
            token = chunk.text or ""
            if token:
                full_reply += token
                # Stream token to client (skip [RESUME_DOWNLOAD] placeholder)
                clean_token = token.replace("[RESUME_DOWNLOAD]", "")
                if clean_token:
                    yield f"data: {json.dumps({'token': clean_token})}\n\n"

        # Determine resume URL after full reply is assembled
        if asked_for_resume and "[RESUME_DOWNLOAD]" in full_reply:
            resume_url = RESUME_URL
        else:
            resume_url = None

        yield f"data: {json.dumps({'done': True, 'resume_url': resume_url})}\n\n"

    except ClientError as e:
        if "RESOURCE_EXHAUSTED" in str(e):
            msg = "I'm getting too many requests right now. Please try again in a few seconds."
        else:
            msg = f"An error occurred: {str(e)}"
        yield f"data: {json.dumps({'error': msg})}\n\n"

    except Exception as e:
        yield f"data: {json.dumps({'error': str(e)})}\n\n"
