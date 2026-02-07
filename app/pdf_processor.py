"""PDF upload and text extraction."""

import pdfplumber
from pathlib import Path


def extract_text(pdf_path: str | Path) -> str:
    """Extract all text from a PDF file."""
    text_parts = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
    return "\n\n".join(text_parts)


def extract_text_from_bytes(pdf_bytes: bytes, filename: str = "upload.pdf") -> str:
    """Extract text from in-memory PDF bytes (for Gradio file uploads)."""
    import tempfile
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=True) as tmp:
        tmp.write(pdf_bytes)
        tmp.flush()
        return extract_text(tmp.name)
