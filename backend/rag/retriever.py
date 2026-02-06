from rag.vectordb import query_db

def retrieve_context(query: str, k: int = 4) -> str:
    # Query vector DB directly with text
    results = query_db(query, k=k)

    # Extract retrieved documents
    documents = results.get("documents", [[]])[0]

    if not documents:
        return ""

    # Join relevant chunks as context
    return "\n\n".join(documents)
