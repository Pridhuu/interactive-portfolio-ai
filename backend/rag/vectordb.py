import chromadb
from config import CHROMA_PERSIST_DIR
from rag.embedder import embed

client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)

collection = client.get_or_create_collection(
    name="portfolio",
    metadata={"hnsw:space": "cosine"}
)


def collection_is_empty() -> bool:
    return collection.count() == 0


def add_documents(docs: list[str], ids: list[str], sections: list[str]):
    """Add documents to ChromaDB with embeddings and metadata."""
    collection.add(
        documents=docs,
        embeddings=[embed(doc) for doc in docs],
        ids=ids,
        metadatas=[{"section": s} for s in sections],
    )


def query_db(query: str, k: int = 4):
    """Query ChromaDB for top-k similar documents."""
    query_embedding = embed(query)
    return collection.query(
        query_embeddings=[query_embedding],
        n_results=k,
    )
