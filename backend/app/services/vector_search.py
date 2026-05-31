import json
import math
from typing import List, Dict

from app.models.document_chunk import DocumentChunk
from app.services.embeddings import create_embedding


def cosine_similarity(vector_a: List[float], vector_b: List[float]) -> float:
    dot_product = sum(a * b for a, b in zip(vector_a, vector_b))

    magnitude_a = math.sqrt(sum(a * a for a in vector_a))
    magnitude_b = math.sqrt(sum(b * b for b in vector_b))

    if magnitude_a == 0 or magnitude_b == 0:
        return 0.0

    return dot_product / (magnitude_a * magnitude_b)


def search_similar_chunks(
    query: str,
    db,
    top_k: int = 3
) -> List[Dict]:
    query_embedding = create_embedding(query)

    chunks = (
        db.query(DocumentChunk)
        .filter(DocumentChunk.embedding.isnot(None))
        .all()
    )

    results = []

    for chunk in chunks:
        chunk_embedding = json.loads(chunk.embedding)
        score = cosine_similarity(query_embedding, chunk_embedding)

        results.append({
            "chunk_id": chunk.id,
            "document_id": chunk.document_id,
            "page_number": chunk.page_number,
            "chunk_index": chunk.chunk_index,
            "content": chunk.content,
            "similarity_score": score
        })

    results.sort(
        key=lambda result: result["similarity_score"],
        reverse=True
    )

    return results[:top_k]