import chromadb
from rag.embedder import embed

client = chromadb.PersistentClient(path="./chroma")
collection = client.get_or_create_collection(
    name="portfolio",
    metadata={"hnsw:space": "cosine"}
)

def add_documents(docs, ids, sections):
    collection.add(
        documents=docs,
        embeddings=[embed(doc) for doc in docs],
        ids=ids,
        metadatas=[{"section": s} for s in sections]
    )


def query_db(query: str, k=4):
    query_embedding = embed(query)
    return collection.query(
        query_embeddings=[query_embedding],
        n_results=k
    )