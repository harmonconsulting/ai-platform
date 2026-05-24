from sentence_transformers import SentenceTransformer
import chromadb

client = chromadb.PersistentClient(path="./chroma")
collection = client.get_or_create_collection(name="knowledge")
model = SentenceTransformer("all-MiniLM-L6-v2")


def chunk_text(text: str, chunk_size: int = 1200, overlap: int = 200):
    chunks = []
    start = 0
    text = text.strip()

    while start < len(text):
        chunk = text[start:start + chunk_size].strip()
        if chunk:
            chunks.append(chunk)
        start += chunk_size - overlap

    return chunks


def add_document(text: str, doc_id: str, filename: str = "unknown"):
    chunks = chunk_text(text)

    ids = []
    embeddings = []
    documents = []
    metadatas = []

    for idx, chunk in enumerate(chunks):
        ids.append(f"{doc_id}-{idx}")
        embeddings.append(model.encode(chunk).tolist())
        documents.append(chunk)
        metadatas.append({
            "doc_id": doc_id,
            "filename": filename,
            "chunk_index": idx
        })

    if ids:
        collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas
        )

    return len(ids)


def search(query: str, k: int = 5):
    embedding = model.encode(query).tolist()

    results = collection.query(
        query_embeddings=[embedding],
        n_results=k
    )

    docs = results.get("documents", [[]])[0]
    metas = results.get("metadatas", [[]])[0]

    return [
        {
            "content": doc,
            "metadata": meta
        }
        for doc, meta in zip(docs, metas)
    ]


def delete_document(doc_id: str):
    results = collection.get(
        where={"doc_id": doc_id}
    )

    ids = results.get("ids", [])

    if ids:
        collection.delete(ids=ids)

    return len(ids)


def delete_document_by_filename(filename: str):
    results = collection.get(
        where={"filename": filename}
    )

    ids = results.get("ids", [])

    if ids:
        collection.delete(ids=ids)

    return len(ids)
