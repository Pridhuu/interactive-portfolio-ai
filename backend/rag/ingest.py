from services.data_loader import load_profile_text
from rag.vectordb import add_documents, collection_is_empty, clear_collection


def ingest_if_needed():
    """
    Ingest documents into ChromaDB only if the collection is empty.
    This prevents re-ingesting on every restart when the DB is already populated.
    """
    if not collection_is_empty():
        print("✅ Vector DB already populated. Skipping ingestion.")
        return

    print("🔄 Vector DB is empty. Starting ingestion...")
    docs = load_profile_text()

    if not docs:
        print("⚠️  No documents found to ingest. Check data/ directory.")
        return

    ids = [f"doc_{i}" for i in range(len(docs))]
    sections = ["profile"] * len(docs)

    add_documents(docs, ids, sections)
    print(f"✅ Ingested {len(docs)} documents into vector DB.")


def ingest():
    """Force re-ingest (wipes and re-inserts). Use for manual resets."""
    docs = load_profile_text()
    ids = [f"doc_{i}" for i in range(len(docs))]
    sections = ["profile"] * len(docs)
    add_documents(docs, ids, sections)
    print(f"✅ Force-ingested {len(docs)} documents.")


def force_reingest():
    """Wipe ChromaDB and re-ingest. Called when Resume.pdf changes."""
    print("🗑️  Clearing stale ChromaDB collection for re-ingestion...")
    clear_collection()
    docs = load_profile_text()
    if not docs:
        print("⚠️  No documents found to ingest. Check data/ directory.")
        return
    ids = [f"doc_{i}" for i in range(len(docs))]
    sections = ["profile"] * len(docs)
    add_documents(docs, ids, sections)
    print(f"✅ Re-ingested {len(docs)} documents into ChromaDB.")


if __name__ == "__main__":
    ingest()
