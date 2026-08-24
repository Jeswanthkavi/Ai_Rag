import pymupdf as fitz


def load_pdf(file_path: str) -> list[dict]:

    pdf = fitz.open(file_path)

    pages = []

    for page_number, page in enumerate(pdf):

        text = page.get_text("text")

        if text.strip():

            pages.append({
                "text": text,
                "page": page_number + 1
            })

    pdf.close()

    return pages


def create_chunks(
    pages: list[dict],
    chunk_size: int = 1000,
    chunk_overlap: int = 200
) -> list[dict]:

    chunks = []

    for page in pages:

        text = page["text"]
        page_number = page["page"]

        start = 0

        while start < len(text):

            end = start + chunk_size

            chunk_text = text[start:end].strip()

            if chunk_text:

                chunks.append({
                    "text": chunk_text,
                    "page": page_number
                })

            start += chunk_size - chunk_overlap

    return chunks