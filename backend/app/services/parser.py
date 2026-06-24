import fitz
import pytesseract
from pathlib import Path
from PIL import Image
import io


def extract_text_from_pdf(file_path: str) -> str:
    pdf_path = Path(file_path)

    if not pdf_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    text_pages = []

    with fitz.open(pdf_path) as doc:
        for page_number, page in enumerate(doc, start=1):
            page_text = page.get_text()

            if not page_text or not page_text.strip():
                page_text = extract_text_with_ocr(page)

            if not page_text or not page_text.strip():
                page_text = "[No text could be extracted from this page.]"

            text_pages.append(f"\n--- Page {page_number} ---\n{page_text}")

    return "\n".join(text_pages)


def extract_text_with_ocr(page) -> str:
    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
    image_bytes = pix.tobytes("png")
    image = Image.open(io.BytesIO(image_bytes))

    text = pytesseract.image_to_string(image)
    return text