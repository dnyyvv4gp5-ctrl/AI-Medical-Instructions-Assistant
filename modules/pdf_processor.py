import pymupdf


def extract_pdf_pages(file_bytes: bytes) -> list[dict]:
    if not file_bytes:
        raise ValueError("The uploaded PDF is empty.")

    try:
        document = pymupdf.open(stream=file_bytes, filetype="pdf")
    except Exception as exc:
        raise ValueError("The uploaded file is not a valid PDF.") from exc

    if document.page_count == 0:
        raise ValueError("The PDF contains no pages.")

    pages = []
    for page_number, page in enumerate(document, start=1):
        text = page.get_text("text").strip()
        if text:
            pages.append({
                "page": page_number,
                "text": text
            })

    document.close()

    if not pages:
        raise ValueError(
            "No readable text found. Scanned PDFs are not supported in this MVP."
        )

    return pages
