"""
refresh_resume.py
-----------------
Run this locally whenever you update Resume.pdf.

  cd backend
  python refresh_resume.py

It will:
  1. Delete the stale resume_parsed.json and resume_pdf.hash
  2. Re-parse Resume.pdf with Gemini -> write fresh resume_parsed.json
  3. Wipe and re-ingest ChromaDB with the new data
  4. Remind you to commit + push the updated files
"""

import sys
from pathlib import Path

# -- Make sure backend/ is on sys.path --------------------------------------
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from dotenv import load_dotenv
load_dotenv()

DATA_DIR      = BASE_DIR / "data"
PARSED_JSON   = DATA_DIR / "resume_parsed.json"
PDF_HASH_FILE = DATA_DIR / "resume_pdf.hash"

# -- Step 1: clear stale cache -----------------------------------------------
for f in [PARSED_JSON, PDF_HASH_FILE]:
    if f.exists():
        f.unlink()
        print(f"[DEL] Deleted {f.name}")

# -- Step 2: re-parse PDF ----------------------------------------------------
from services.resume_parser import ensure_resume_json_exists
pdf_parsed = ensure_resume_json_exists()

if not pdf_parsed:
    print("[ERR] Re-parse did not succeed. Check Resume.pdf exists and GOOGLE_API_KEY is set.")
    sys.exit(1)

# -- Step 3: wipe + re-ingest ChromaDB --------------------------------------
from rag.ingest import force_reingest
force_reingest()

# -- Done --------------------------------------------------------------------
print()
print("[OK] Done! Now commit and push the updated files:")
print("   git add backend/data/resume_parsed.json backend/data/resume_pdf.hash backend/chroma/")
print('   git commit -m "Refresh resume data and ChromaDB"')
print("   git push")
