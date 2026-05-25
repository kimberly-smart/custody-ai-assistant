from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.parser import extract_text_from_pdf

router = APIRouter(
    prefix="/documents",
    tags=["Documents"]
)

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
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
    extracted_text = extract_text_from_pdf(file_path)

    return {
        "message": "File uploaded successfully",
        "filename": file.filename,
        "saved_path": str(file_path),
        "size_bytes": len(content),
        "text_preview": extracted_text[:1000],
        "text_length": len(extracted_text) 
    }