from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Form
from app.services.parser import extract_text_from_pdf
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.document import Document
from typing import Optional

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
    db.commit()
    db.refresh(document)

    return {
        "message": "File uploaded and saved successfully",
        "document_id": document.id,
        "filename": file.filename,
        "saved_path": str(file_path),
        "size_bytes": len(content),
        "text_preview": extracted_text[:1000],
        "text_length": len(extracted_text) 
    }



@router.get("/")
def get_documents(db: Session = Depends(get_db)):
    documents = db.query(Document).all()

    return documents


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

@router.delete("/{document_id}")
def delete_document(document_id: int, db: Session = Depends(get_db)):
    document = db.query(Document).filter(Document.id == document_id).first()

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found."
        )

    db.delete(document)
    db.commit()

    return {
        "message": "Document deleted successfully",
        "document_id": document_id
    }