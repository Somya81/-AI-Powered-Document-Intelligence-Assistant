
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

model = SentenceTransformer("all-MiniLM-L6-v2")


def create_chunks(pages, chunk_size=700, overlap=120):

    chunks = []

    for page in pages:

        text = page["text"]
        start = 0

        while start < len(text):

            end = start + chunk_size
            chunk_text = text[start:end]

            if chunk_text.strip():

                chunks.append({
                    "page": page["page"],
                    "text": chunk_text
                })

            start += chunk_size - overlap

    return chunks


def create_vector_store(pages):

    chunks = create_chunks(pages)

    if not chunks:
        return None, []

    texts = [chunk["text"] for chunk in chunks]

    embeddings = model.encode(
        texts,
        normalize_embeddings=True
    )

    embeddings = np.array(embeddings, dtype="float32")

    dimension = embeddings.shape[1]

    index = faiss.IndexFlatIP(dimension)
    index.add(embeddings)

    return index, chunks


def search_documents(query, index, chunks, top_k=5):

    if index is None or not chunks:
        return []

    query_embedding = model.encode(
        [query],
        normalize_embeddings=True
    )

    query_embedding = np.array(
        query_embedding,
        dtype="float32"
    )

    total_chunks = len(chunks)

    scores, indices = index.search(
        query_embedding,
        min(top_k, total_chunks)
    )

    results = []

    for score, idx in zip(scores[0], indices[0]):

        if 0 <= idx < total_chunks:

            result = chunks[idx].copy()
            result["score"] = float(score)

            results.append(result)

    return results
