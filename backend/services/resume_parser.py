"""
resume_parser.py
────────────────
Parses resume.pdf ONCE using Gemini and saves the result to data/resume_parsed.json.

Rules:
- If data/resume_parsed.json already exists AND the PDF hash matches → skip (use cache).
- If PDF hash has changed (or JSON missing) → re-parse PDF with Gemini, update cache.

The PDF hash is stored in data/resume_pdf.hash so changes are detected automatically
on every restart without needing manual file deletion.
"""

import hashlib
import json
import time
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()

from google import genai
from google.genai import types

BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static"
DATA_DIR   = BASE_DIR / "data"

RESUME_PDF   = STATIC_DIR / "Resume.pdf"
PARSED_JSON  = DATA_DIR   / "resume_parsed.json"
PDF_HASH_FILE = DATA_DIR  / "resume_pdf.hash"


def _parse_pdf_with_gemini() -> dict:
    """Upload the resume PDF to Gemini and extract structured JSON."""
    client = genai.Client()

    print("[PDF] Uploading Resume.pdf to Gemini for one-time parsing...")

    with open(RESUME_PDF, "rb") as f:
        uploaded = client.files.upload(
            file=f,
            config=types.UploadFileConfig(
                mime_type="application/pdf",
                display_name="Resume",
            ),
        )

    # Wait until Gemini finishes processing the file
    max_wait, waited = 60, 0
    while uploaded.state and uploaded.state.name == "PROCESSING":
        if waited >= max_wait:
            raise TimeoutError("Gemini file processing timed out.")
        time.sleep(2)
        waited += 2
        uploaded = client.files.get(name=uploaded.name)

    extraction_prompt = """
You are a resume parser. Extract ALL information from this resume PDF and return it as a single valid JSON object.

The JSON must have these top-level keys (include only what is present):
- personal_information: { name, email, phone, location, linkedin, github, website }
- summary: string
- education: list of { institution, degree, field, duration, gpa }
- experience: list of { role, organization, duration, details (list of strings) }
- projects: list of { title, description (list of strings), language, technologies, duration }
- positions_of_responsibility: list of { role, organization, details (list of strings) }
- technical_skills: { languages (list), technologies_frameworks (list), tools (list) }
- certifications: list of strings
- achievements: list of strings

Rules:
- Output ONLY the raw JSON object. No markdown fences, no explanation.
- Each "details" or "description" must be a list of strings (bullet points).
- Preserve ALL information from the resume. Do not omit anything.
"""

    response = client.models.generate_content(
        model="models/gemini-flash-lite-latest",
        contents=[
            types.Part.from_uri(file_uri=uploaded.uri, mime_type="application/pdf"),
            extraction_prompt,
        ],
    )

    raw = response.text.strip()

    # Strip markdown code fences if Gemini wraps output in them
    if raw.startswith("```"):
        lines = raw.splitlines()
        raw = "\n".join(
            line for line in lines
            if not line.strip().startswith("```")
        ).strip()

    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"[WARN] Gemini returned invalid JSON: {e}")
        print("Raw output (first 500 chars):", raw[:500])
        raise


def _get_pdf_hash() -> str:
    """Compute the MD5 hash of the current Resume.pdf."""
    h = hashlib.md5()
    with open(RESUME_PDF, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def _pdf_has_changed() -> bool:
    """Return True if Resume.pdf is new or differs from the stored hash."""
    if not PDF_HASH_FILE.exists():
        return True  # No hash stored yet → treat as changed
    return PDF_HASH_FILE.read_text().strip() != _get_pdf_hash()


def _save_pdf_hash():
    """Persist the current Resume.pdf hash for future change detection."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    PDF_HASH_FILE.write_text(_get_pdf_hash())


def ensure_resume_json_exists() -> bool:
    """
    Called once at backend startup.

    - If resume_parsed.json exists AND PDF hash unchanged → skip (use cache).
    - If PDF has changed (or JSON missing) → re-parse, update cache + hash.
    - If no Resume.pdf found → warn and continue (profile.json will still be used).

    Returns True if a fresh parse was performed (caller should re-ingest ChromaDB).
    """
    if not RESUME_PDF.exists():
        print("[WARN] No Resume.pdf found in static/. Skipping PDF parsing.")
        return False

    if PARSED_JSON.exists() and not _pdf_has_changed():
        print("[OK] resume_parsed.json is up-to-date (PDF unchanged). Skipping re-parse.")
        return False

    if PARSED_JSON.exists():
        print("[UPDATE] Resume.pdf has changed -- deleting stale cache and re-parsing...")
        PARSED_JSON.unlink()
    else:
        print("[PARSE] resume_parsed.json not found. Parsing PDF with Gemini (one-time)...")

    try:
        data = _parse_pdf_with_gemini()
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        json_str = json.dumps(data, indent=2, ensure_ascii=True)  # ASCII-safe for Windows cp1252
        with open(PARSED_JSON, "w", encoding="utf-8") as f:
            f.write(json_str)
        _save_pdf_hash()  # Update hash ONLY after successful parse
        print(f"[OK] Parsed resume saved to {PARSED_JSON.name}")
        return True  # Signal: ChromaDB needs re-ingest
    except Exception as e:
        print(f"[ERR] Failed to parse resume PDF: {e}")
        print("   Chat will continue using profile.json only.")
        return False
