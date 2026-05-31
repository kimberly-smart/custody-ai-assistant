import re
from typing import List, Dict


def split_text_into_chunks(
    extracted_text: str,
    chunk_size: int = 800,
    overlap: int = 100
) -> List[Dict]:
    chunks = []

    page_pattern = r"--- Page (\d+) ---"
    parts = re.split(page_pattern, extracted_text)


    # ["", "1", "page 1 text", "2", "page 2 text", .........]
    for i in range(1, len(parts), 2):
        page_number = int(parts[i])
        page_text = parts[i + 1].strip()

        if not page_text:
            continue

        start = 0
        chunk_index = 0

        while start < len(page_text):
            end = start + chunk_size
            chunk_content = page_text[start:end].strip()

            if chunk_content:
                chunks.append({
                    "page_number": page_number,
                    "chunk_index": chunk_index,
                    "content": chunk_content
                })

            chunk_index += 1
            start += chunk_size - overlap

    return chunks