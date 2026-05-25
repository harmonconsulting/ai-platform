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


def add_document(
    text: str,
    doc_id: str = "unknown",
    filename: str = "unknown",
    team_slug: str = "global",
):
    chunks = chunk_text(text)

    ids = []
    documents = []
    embeddings = []
    metadatas = []

    for i, chunk in enumerate(chunks):
        ids.append(f"{team_slug}:{doc_id}:{i}")
        documents.append(chunk)
        embeddings.append(model.encode(chunk).tolist())
        metadatas.append({
            "doc_id": doc_id,
            "filename": filename,
            "chunk_index": i,
            "team_slug": team_slug,
        })

    if ids:
        collection.upsert(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
        )

    return len(ids)


def search(query: str, k: int = 5, team_slug: str = "global"):
    embedding = model.encode(query).tolist()

    results = collection.query(
        query_embeddings=[embedding],
        n_results=k,
        where={"team_slug": team_slug},
    )

    docs = results.get("documents", [[]])[0]
    metas = results.get("metadatas", [[]])[0]

    return [
        {
            "content": doc,
            "metadata": meta or {},
        }
        for doc, meta in zip(docs, metas)
    ]


def delete_document_by_filename(filename: str, team_slug: str = "global"):
    results = collection.get(
        where={
            "$and": [
                {"filename": filename},
                {"team_slug": team_slug},
            ]
        }
    )

    ids = results.get("ids", [])

    if ids:
        collection.delete(ids=ids)

    return len(ids)


def reset_team_knowledge(team_slug: str):
    results = collection.get(where={"team_slug": team_slug})
    ids = results.get("ids", [])

    if ids:
        collection.delete(ids=ids)

    return len(ids)
