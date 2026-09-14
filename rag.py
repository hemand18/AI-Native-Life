import chromadb

client = chromadb.PersistentClient(path="chroma_db")
collection = client.get_or_create_collection(name="documents")

def add_document(doc_id, text, chunk_size=500):
    # naive chunking: split text into fixed-size pieces
    chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
    ids = [f"{doc_id}_{i}" for i in range(len(chunks))]
    collection.add(documents=chunks, ids=ids)

def query_documents(query_text, n_results=3):
    results = collection.query(query_texts=[query_text], n_results=n_results)
    return results["documents"][0] if results["documents"] else []