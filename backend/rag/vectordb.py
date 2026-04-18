from __future__ import annotations
from config import CHROMA_PERSIST_DIR
from rag.embedder import embed

# Lazy — not initialized until first DB access
_client = None
_collection = None

def _get_collection():
    global _client, _collection
    if _collection is None:
        import chromadb
        _client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
        _collection = _client.get_or_create_collection(
            name="portfolio",
            metadata={"hnsw:space": "cosine"}
        )
    return _collection


def collection_is_empty() -> bool:
    return _get_collection().count() == 0


def clear_collection():
    """Delete all documents from the ChromaDB collection (for forced re-ingest)."""
    col = _get_collection()
    existing = col.get()
    if existing["ids"]:
        col.delete(ids=existing["ids"])
        print(f"[DEL] Cleared {len(existing['ids'])} documents from ChromaDB.")
    else:
        print("[INFO] ChromaDB collection was already empty.")


def add_documents(docs: list[str], ids: list[str], sections: list[str]):
    """Add documents to ChromaDB with embeddings and metadata."""
    _get_collection().add(
        documents=docs,
        embeddings=[embed(doc) for doc in docs],
        ids=ids,
        metadatas=[{"section": s} for s in sections],
    )


def query_db(query: str, k: int = 3) -> dict:
    """Query ChromaDB. Returns empty safely if collection not yet ingested."""
    if collection_is_empty():
        return {"documents": [[]], "metadatas": [[]], "distances": [[]]}
    query_embedding = embed(query)
    return _get_collection().query(
        query_embeddings=[query_embedding],
        n_results=k,
    )
