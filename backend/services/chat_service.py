import json
from pathlib import Path
from google import genai
from google.genai.errors import ClientError

from config import RESUME_URL
from rag.retriever import retrieve_context

client = genai.Client()
MODEL_NAME = "models/gemini-flash-latest"

BASE_DIR = Path(__file__).resolve().parent.parent
PROMPT_FILE = BASE_DIR / "prompts" / "system_prompt.txt"

# ── Prompt cache: re-read only when file changes ─────────────────────────────
_prompt_cache: str = ""
_prompt_mtime: float = 0.0

def get_system_prompt() -> str:
    global _prompt_cache, _prompt_mtime
    mtime = PROMPT_FILE.stat().st_mtime
    if mtime != _prompt_mtime:
        _prompt_cache = PROMPT_FILE.read_text(encoding="utf-8")
        _prompt_mtime = mtime
    return _prompt_cache


# ── Streaming chat ────────────────────────────────────────────────────────────
def stream_chat(user_message: str):
    """
    Yield SSE-formatted chunks:
      data: {"token": "..."}\n\n
      data: {"done": true, "resume_url": "..."|null}\n\n
      data: {"error": "..."}\n\n
    """
    try:
        context = retrieve_context(user_message, k=4)
        if not context.strip():
            context = "No relevant information found in portfolio data."

        prompt = f"""{get_system_prompt()}

=== RELEVANT PORTFOLIO CONTEXT ===
{context}

=== USER QUESTION ===
{user_message}
"""

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
                clean_token = token.replace("[RESUME_DOWNLOAD]", "")
                if clean_token:
                    yield f"data: {json.dumps({'token': clean_token})}\n\n"

        resume_url = None
        if asked_for_resume and "[RESUME_DOWNLOAD]" in full_reply:
            resume_url = RESUME_URL

        yield f"data: {json.dumps({'done': True, 'resume_url': resume_url})}\n\n"

    except ClientError as e:
        if "RESOURCE_EXHAUSTED" in str(e):
            msg = "I'm getting too many requests right now. Please try again in a few seconds."
        else:
            msg = f"An error occurred: {e}"
        yield f"data: {json.dumps({'error': msg})}\n\n"

    except Exception as e:
        yield f"data: {json.dumps({'error': str(e)})}\n\n"
