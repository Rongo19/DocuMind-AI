import os
import chromadb
from sentence_transformers import SentenceTransformer
from groq import Groq
from app.core.config import GROQ_API_KEY, CHROMA_DIR

# ── init ───────────────────────────────────────────────────────────────────
embedder = SentenceTransformer("all-MiniLM-L6-v2")

chroma_client = chromadb.PersistentClient(path=CHROMA_DIR)
collection = chroma_client.get_or_create_collection(
    name="documents",
    metadata={"hnsw:space": "cosine"}
)

groq_client = Groq(api_key=GROQ_API_KEY)


# ── chunking ───────────────────────────────────────────────────────────────
def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        end = start + chunk_size
        chunk = " ".join(words[start:end])
        if chunk.strip():
            chunks.append(chunk)
        start = end - overlap
    return chunks


# ── indexing ───────────────────────────────────────────────────────────────
def index_document(doc_id: str, filename: str, pages: list[dict]):
    all_chunks = []
    all_embeddings = []
    all_ids = []
    all_metadata = []

    for page in pages:
        text = page["text"]
        if not text.strip():
            continue

        chunks = chunk_text(text)
        for i, chunk in enumerate(chunks):
            chunk_id = f"{doc_id}_p{page['page_num']}_c{i}"
            embedding = embedder.encode(chunk).tolist()

            all_ids.append(chunk_id)
            all_chunks.append(chunk)
            all_embeddings.append(embedding)
            all_metadata.append({
                "doc_id": doc_id,
                "filename": filename,
                "page_num": page["page_num"],
                "image_url": page["image_url"],
            })

    if all_ids:
        collection.upsert(
            ids=all_ids,
            documents=all_chunks,
            embeddings=all_embeddings,
            metadatas=all_metadata,
        )

    return len(all_ids)


# ── retrieval ──────────────────────────────────────────────────────────────
def retrieve_chunks(query: str, top_k: int = 5) -> list[dict]:
    query_embedding = embedder.encode(query).tolist()

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=["documents", "metadatas", "distances"]
    )

    chunks = []
    for i in range(len(results["ids"][0])):
        chunks.append({
            "text": results["documents"][0][i],
            "metadata": results["metadatas"][0][i],
            "score": 1 - results["distances"][0][i],
        })

    return chunks


# ── answer generation ──────────────────────────────────────────────────────
def generate_answer(query: str, chunks: list[dict]) -> dict:
    if not chunks:
        return {
            "answer": "I could not find any relevant information in the uploaded documents.",
            "citations": []
        }

    # Build context string
    context = ""
    for i, chunk in enumerate(chunks):
        meta = chunk["metadata"]
        context += f"[Source {i+1}: {meta['filename']}, Page {meta['page_num']}]\n"
        context += chunk["text"] + "\n\n"

    prompt = f"""You are a helpful assistant that answers questions based strictly on the provided document context.

Rules:
- Answer only using the context below
- Cite sources inline like this: [filename, Page X]
- If the answer is not in the context, say "I could not find this information in the uploaded documents."
- Do not make up information

Context:
{context}

Question: {query}

Answer:"""

    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant. Answer questions using only the provided context and always cite your sources."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.2,
    )

    answer = response.choices[0].message.content.strip()

    # Build citations list
    citations = []
    seen = set()
    for chunk in chunks:
        meta = chunk["metadata"]
        key = f"{meta['doc_id']}_p{meta['page_num']}"
        if key not in seen:
            seen.add(key)
            citations.append({
                "filename": meta["filename"],
                "page_num": meta["page_num"],
                "image_url": meta["image_url"],
                "doc_id": meta["doc_id"],
            })

    return {
        "answer": answer,
        "citations": citations
    }


# ── main query function ────────────────────────────────────────────────────
def query_documents(query: str, top_k: int = 5) -> dict:
    chunks = retrieve_chunks(query, top_k)

    # Filter low relevance chunks
    chunks = [c for c in chunks if c["score"] > 0.1]

    return generate_answer(query, chunks)