from services.data_loader import load_profile_text
from rag.vectordb import add_documents

def ingest():
    docs = load_profile_text()
    ids = [f"doc_{i}" for i in range(len(docs))]
    sections = ["profile"] * len(docs)

    add_documents(docs, ids, sections)
    print("✅ Ingestion completed")

if __name__ == "__main__":
    ingest()
