try:
    import chromadb
except ImportError:  # pragma: no cover - optional dependency during local setup
    chromadb = None

if chromadb is not None:
    client = chromadb.PersistentClient(path="chroma_db")
    collection = client.get_or_create_collection(name="documents")
else:
    client = None
    collection = None


def add_document(doc_id, text, chunk_size=500):
    if collection is None:
        return

    # naive chunking: split text into fixed-size pieces
    chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
    ids = [f"{doc_id}_{i}" for i in range(len(chunks))]
    collection.add(documents=chunks, ids=ids)


def query_documents(query_text, n_results=3):
    if collection is None:
        return []

    results = collection.query(query_texts=[query_text], n_results=n_results)
    return results["documents"][0] if results["documents"] else []