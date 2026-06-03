from typing import Optional

from fastapi import APIRouter, Depends, Form
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.services.rag import generate_grounded_answer
from app.services.vector_search import search_similar_chunks


router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)


@router.post("/ask")
def ask_question(
    question: str = Form(...),
    top_k: int = Form(3),
    db: Session = Depends(get_db)
):
    retrieved_chunks = search_similar_chunks(
        query=question,
        db=db,
        top_k=top_k
    )

    answer = generate_grounded_answer(
        question=question,
        retrieved_chunks=retrieved_chunks
    )

    sources = [
        {
            "chunk_id": chunk["chunk_id"],
            "document_id": chunk["document_id"],
            "filename": chunk["filename"],
            "document_type": chunk["document_type"],
            "page_number": chunk["page_number"],
            "similarity_score": chunk["similarity_score"]
        }
        for chunk in retrieved_chunks
    ]

    return {
        "question": question,
        "answer": answer,
        "sources": sources
    }