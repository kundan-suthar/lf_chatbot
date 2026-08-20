from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import DocumentChunk
from app.services.llm.embeddings import EmbeddingClient


def retrieve_relevant_chunks(
    db: Session,
    query: str,
    top_k: int = 5,
):
    """
    Convert the query into an embedding and retrieve
    the most relevant document chunks using pgvector.
    """

    embedding_client = EmbeddingClient()

    query_embedding = embedding_client.embed(query)

    # pgvector cosine distance
    distance = DocumentChunk.embedding.cosine_distance(
        query_embedding
    )

    stmt = (
        select(
            DocumentChunk,
            distance.label("distance"),
        )
        .join(DocumentChunk.document)
        .where(
            DocumentChunk.document.has(
                is_active=True,
                status="READY",
            )
        )
        .order_by(distance)
        .limit(top_k)
    )

    results = db.execute(stmt).all()

    retrieved_chunks = []

    for chunk, distance_value in results:

        retrieved_chunks.append(
            {
                "chunk_id": chunk.id,
                "document_id": chunk.document_id,
                "content": chunk.content,
                "similarity": 1 - distance_value,
                "metadata": chunk.chunk_metadata,
            }
        )

    return retrieved_chunks