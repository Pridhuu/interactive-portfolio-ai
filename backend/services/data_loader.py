import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"


def load_profile_text():
    docs = []
    ids = []
    sections = []

    for file in DATA_DIR.iterdir():
        if file.suffix == ".json":
            data = json.loads(file.read_text(encoding="utf-8"))

            for section, content in data.items():
                docs.append(
                    f"Information about {section.replace('_', ' ')}:\n{to_text(content)}"
                )
                ids.append(f"{file.stem}_{section}")
                sections.append(section)

    return docs, ids, sections


def to_text(data):
    if isinstance(data, dict):
        return "\n".join(f"{k}: {to_text(v)}" for k, v in data.items())
    if isinstance(data, list):
        return "\n".join(to_text(item) for item in data)
    return str(data)
