"""Real, locally-running text extraction for AI field extraction.

No external service calls: PDF text comes from pdfplumber, image text from
Tesseract OCR (Dutch + English language data). This is the "OCR Service"
step described in docs/04 section 5.1, implemented with a lightweight local
engine rather than the full GPU OCR/Vision pipeline docs/04 envisions for
the on-prem AI server - a reasonable substitute until that infrastructure
is wired up (see PROGRESS.md).
"""

from __future__ import annotations

from pathlib import Path

import pdfplumber
import pytesseract
from PIL import Image

MAX_PAGES = 10


def extract_text(file_path: Path, extension: str) -> str:
    ext = extension.lower().lstrip(".")
    if ext == "pdf":
        return _extract_pdf_text(file_path)
    if ext in ("jpg", "jpeg"):
        return _extract_image_text(file_path)
    return ""


def _extract_pdf_text(file_path: Path) -> str:
    pages_text: list[str] = []
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages[:MAX_PAGES]:
            text = page.extract_text() or ""
            pages_text.append(text)
    return "\n".join(pages_text)


def _extract_image_text(file_path: Path) -> str:
    with Image.open(file_path) as img:
        return pytesseract.image_to_string(img, lang="nld+eng")
