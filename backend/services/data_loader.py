import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"


def load_profile_text() -> list[str]:
    """
    Load all JSON files from the data/ directory and convert them
    to human-readable text chunks for vector DB ingestion.

    Includes both profile.json and resume_parsed.json (if it exists).
    """
    docs = []

    json_files = sorted(DATA_DIR.glob("*.json"))
    if not json_files:
        print("⚠️  No JSON files found in data/")
        return docs

    for file in json_files:
        try:
            data = json.loads(file.read_text(encoding="utf-8"))
            source = file.stem  # e.g. "profile" or "resume_parsed"

            for section, content in data.items():
                docs.append(
                    f"[Source: {source}] Information about {section.replace('_', ' ')}:\n{to_text(content)}"
                )
        except Exception as e:
            print(f"⚠️  Could not load {file.name}: {e}")

    return docs


def to_text(data) -> str:
    """Recursively converts nested dict/list/value to a flat text string."""
    if isinstance(data, dict):
        return "\n".join(f"{k}: {to_text(v)}" for k, v in data.items())
    if isinstance(data, list):
        return "\n".join(f"- {to_text(item)}" for item in data)
    return str(data)
