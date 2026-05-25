import fitz
from pathlib import Path


def extract_text_from_pdf(file_path: str) -> str:
    pdf_path = Path(file_path)

    if not pdf_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    text_pages = []

    with fitz.open(pdf_path) as doc:
        for page_number, page in enumerate(doc, start=1):
            page_text = page.get_text()
            text_pages.append(f"\n--- Page {page_number} ---\n{page_text}")

    return "\n".join(text_pages)