from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Form
from app.services.parser import extract_text_from_pdf
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.document import Document
from typing import Optional
from app.models.document_chunk import DocumentChunk
from app.services.chunker import split_text_into_chunks
import json
from app.services.embeddings import create_embedding
from app.services.vector_search import search_similar_chunks

router = APIRouter(
    prefix="/documents",
    tags=["Documents"]
)

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    document_type: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed."
        )

    file_path = UPLOAD_DIR / file.filename
    content = await file.read()

    with open(file_path, "wb") as f:
        f.write(content)

    # Extract text from the uploaded PDF
    extracted_text = extract_text_from_pdf(str(file_path))

    document = Document(
        filename=file.filename,
        saved_path=str(file_path),
        file_size=len(content),
        extracted_text=extracted_text,
        document_type=document_type
    )

    db.add(document)
    db.flush()
    db.refresh(document)

    chunks = split_text_into_chunks(extracted_text)

    for chunk in chunks:
        embedding = create_embedding(chunk["content"])
        document_chunk = DocumentChunk(
            document_id=document.id,
            page_number=chunk["page_number"],
            chunk_index=chunk["chunk_index"],
            content=chunk["content"],
            embedding=json.dumps(embedding)
        )
        db.add(document_chunk)

    db.commit()

    return {
        "message": "File uploaded and saved successfully",
        "document_id": document.id,
        "filename": document.filename,
        "saved_path": document.saved_path,
        "size_bytes": document.file_size,
        "document_type": document.document_type,
        "text_preview": document.extracted_text[:1000],
        "text_length": len(document.extracted_text),
        "chunk_count": len(chunks),
        "embedding_created": True
    }



@router.get("/")
def get_documents(db: Session = Depends(get_db)):
    documents = db.query(Document).all()

    return [
        {
            "id": document.id,
            "filename": document.filename,
            "file_size": document.file_size,
            "document_type": document.document_type,
            "created_at": document.created_at,
            "text_length": len(document.extracted_text),
            "text_preview": document.extracted_text[:300]
        }
        for document in documents
        ]


@router.get("/search")
def search_document_chunks(query: str, db: Session = Depends(get_db)):
    chunks = (
        db.query(DocumentChunk)
        .filter(DocumentChunk.content.ilike(f"%{query}%"))
        .all()
    )

    return [
        {
            "chunk_id": chunk.id,
            "document_id": chunk.document_id,
            "page_number": chunk.page_number,
            "chunk_index": chunk.chunk_index,
            "content": chunk.content
        }
        for chunk in chunks
    ]


@router.get("/semantic-search")
def semantic_search(
    query: str,
    top_k: int = 3,
    db: Session = Depends(get_db)
):
    results = search_similar_chunks(
        query=query,
        db=db,
        top_k=top_k
    )

    return {
        "query": query,
        "results": results
    }

@router.get("/{document_id}/text")
def get_document_text(document_id: int, db: Session = Depends(get_db)):
    document = db.query(Document).filter(Document.id == document_id).first()

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found."
        )

    return {
        "id": document.id,
        "filename": document.filename,
        "text_length": len(document.extracted_text),
        "extracted_text": document.extracted_text
    }

@router.get("/{document_id}/chunks")
def get_document_chunks(document_id: int, db: Session = Depends(get_db)):
    document = db.query(Document).filter(Document.id == document_id).first()

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found."
        )

    chunks = (
        db.query(DocumentChunk)
        .filter(DocumentChunk.document_id == document_id)
        .order_by(DocumentChunk.page_number, DocumentChunk.chunk_index)
        .all()
    )

    return [
        {
            "id": chunk.id,
            "document_id": chunk.document_id,
            "page_number": chunk.page_number,
            "chunk_index": chunk.chunk_index,
            "content": chunk.content
        }
        for chunk in chunks
    ]

@router.get("/{document_id}")
def get_document(document_id: int, db: Session = Depends(get_db)):
    document = db.query(Document).filter(Document.id == document_id).first()

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found."
        )

    return {
        "id": document.id,
        "filename": document.filename,
        "saved_path": document.saved_path,
        "file_size": document.file_size,
        "document_type": document.document_type,
        "created_at": document.created_at,
        "text_length": len(document.extracted_text),
        "text_preview": document.extracted_text[:1000]
    }


@router.delete("/{document_id}")
def delete_document(document_id: int, db: Session = Depends(get_db)):
    document = db.query(Document).filter(Document.id == document_id).first()

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found."
        )
    
    db.query(DocumentChunk).filter(
        DocumentChunk.document_id == document_id
    ).delete()
    db.delete(document)
    db.commit()

    return {
        "message": "Document deleted successfully",
        "document_id": document_id
    }