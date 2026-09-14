from rag import add_document

with open("sample.md", "r", encoding="utf-8") as f:
    text = f.read()

add_document("sample_doc", text)
print("Document added to the RAG store.")