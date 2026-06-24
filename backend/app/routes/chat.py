from typing import Optional

from fastapi import APIRouter, Depends, Form
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.services.rag import generate_grounded_answer
from app.services.vector_search import search_similar_chunks
from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.services.summarizer import generate_document_summary


router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)

def is_summary_request(question: str) -> bool:
    summary_keywords = [
        "summarize",
        "summary",
        "briefly summarize",
        "what does this document contain",
        "what is this document about",
        "overview",
    ]

    normalized_question = question.lower()
    return any(keyword in normalized_question for keyword in summary_keywords)


def find_document_for_summary(question: str, db: Session):
    documents = db.query(Document).order_by(Document.created_at.desc()).all()

    if not documents:
        return None

    normalized_question = question.lower()

    for document in documents:
        filename = document.filename.lower()
        filename_without_extension = filename.replace(".pdf", "")

        if filename in normalized_question:
            return document

        if filename_without_extension in normalized_question:
            return document

    return documents[0]

@router.post("/ask")
def ask_question(
    question: str = Form(...),
    top_k: int = Form(3),
    db: Session = Depends(get_db)
):
    if is_summary_request(question):

        document = find_document_for_summary(question, db)

        if not document:

            return {

                "question": question,

                "answer": "No uploaded documents were found to summarize.",

                "sources": [],

            }

        chunks = (

            db.query(DocumentChunk)

            .filter(DocumentChunk.document_id == document.id)

            .order_by(DocumentChunk.page_number, DocumentChunk.chunk_index)

            .all()

        )

        chunk_data = [

            {

                "page_number": chunk.page_number,

                "chunk_index": chunk.chunk_index,

                "content": chunk.content,

            }

            for chunk in chunks

        ]

        summary = generate_document_summary(

            filename=document.filename,

            chunks=chunk_data,

        )

        page_numbers = sorted({chunk.page_number for chunk in chunks})

        return {

            "question": question,

            "answer": summary,

            "sources": [

                {

                    "chunk_id": f"summary-{document.id}",

                    "document_id": document.id,

                    "filename": document.filename,

                    "document_type": document.document_type,

                    "page_number": f"{page_numbers[0]}-{page_numbers[-1]}" if page_numbers else "N/A",

                    "similarity_score": None,

                }

            ],

        }
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