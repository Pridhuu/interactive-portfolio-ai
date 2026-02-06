import os
import chromadb
from rag.embedder import embed

# Get persistence path from environment
CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./chroma")

client = chromadb.PersistentClient(
    path=CHROMA_PERSIST_DIR
)

collection = client.get_or_create_collection(
    name="portfolio",
    metadata={"hnsw:space": "cosine"}
)

def add_documents(docs, ids, sections):
    """
    Add documents to ChromaDB with embeddings and metadata.
    """
    collection.add(
        documents=docs,
        embeddings=[embed(doc) for doc in docs],
        ids=ids,
        metadatas=[{"section": s} for s in sections]
    )

def query_db(query: str, k: int = 4):
    """
    Query ChromaDB for top-k similar documents.
    """
    query_embedding = embed(query)
    return collection.query(
        query_embeddings=[query_embedding],
        n_results=k
    )

def reset_db():
    """
    Reset the ChromaDB collection.
    """
    try:
        client.delete_collection("portfolio")
    except Exception:
        pass
    
    global collection
    collection = client.get_or_create_collection(
        name="portfolio",
        metadata={"hnsw:space": "cosine"}
    )



# import chromadb
# from rag.embedder import embed

# client = chromadb.PersistentClient(path="./chroma")
# collection = client.get_or_create_collection(
#     name="portfolio",
#     metadata={"hnsw:space": "cosine"}
# )

# def add_documents(docs, ids, sections):
#     collection.add(
#         documents=docs,
#         embeddings=[embed(doc) for doc in docs],
#         ids=ids,
#         metadatas=[{"section": s} for s in sections]
#     )


# def query_db(query: str, k=4):
#     query_embedding = embed(query)
#     return collection.query(
#         query_embeddings=[query_embedding],
#         n_results=k
#     )

