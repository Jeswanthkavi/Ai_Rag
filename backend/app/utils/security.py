import re


MAX_FILE_SIZE = 10 * 1024 * 1024


def sanitize_filename(
    filename: str
) -> str:

    if not filename:

        return "document.pdf"

    filename = filename.strip()

    filename = re.sub(
        r"[^a-zA-Z0-9._-]",
        "_",
        filename
    )

    if not filename.lower().endswith(
        ".pdf"
    ):

        filename += ".pdf"

    return filename


def is_pdf_signature(
    content: bytes
) -> bool:

    return content.startswith(
        b"%PDF"
    )