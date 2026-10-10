import re
from typing import List, Dict, Any
import pymupdf  # PyMuPDF
from app.config import settings


def extract_text_from_pdf(file_path: str) -> List[Dict[str, Any]]:
    """
    Extract text from a PDF file page by page using PyMuPDF.
    Returns list of dicts: [{"page": 1, "text": "..."}]
    """
    pages_data = []
    doc = pymupdf.open(file_path)
    try:
        for page_idx in range(len(doc)):
            page = doc[page_idx]
            page_text = page.get_text("text") or ""
            # Clean excessive whitespaces while preserving paragraph breaks
            cleaned_text = re.sub(r'[ \t]+', ' ', page_text).strip()
            if cleaned_text:
                pages_data.append({
                    "page": page_idx + 1,
                    "text": cleaned_text
                })
    finally:
        doc.close()
    return pages_data


def extract_text_from_txt(file_path: str) -> List[Dict[str, Any]]:
    """
    Extract text from a plain text or markdown file.
    Returns list with a single page.
    """
    with open(file_path, "r", encoding="utf-8", errors="replace") as f:
        text = f.read()

    cleaned_text = re.sub(r'[ \t]+', ' ', text).strip()
    return [{"page": 1, "text": cleaned_text}]


def chunk_pages_text(
    pages_data: List[Dict[str, Any]],
    chunk_size: int = settings.CHUNK_SIZE,
    chunk_overlap: int = settings.CHUNK_OVERLAP
) -> List[Dict[str, Any]]:
    """
    Segment extracted pages into overlapping chunks while preserving page metadata.
    Returns list of dicts: [{"chunk_index": 0, "page_number": 1, "content": "...", "token_count": 42}]
    """
    chunks = []
    chunk_idx = 0

    for page_item in pages_data:
        page_num = page_item["page"]
        text = page_item["text"]

        if not text:
            continue

        # Split into paragraphs
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        if not paragraphs:
            paragraphs = [text]

        current_chunk = ""

        for para in paragraphs:
            # If paragraph itself is longer than chunk_size, split by sentences
            if len(para) > chunk_size:
                sentences = re.split(r'(?<=[.!?])\s+', para)
                for sent in sentences:
                    if len(current_chunk) + len(sent) + 1 <= chunk_size:
                        current_chunk = f"{current_chunk} {sent}".strip()
                    else:
                        if current_chunk:
                            token_estimate = max(1, len(current_chunk.split()))
                            chunks.append({
                                "chunk_index": chunk_idx,
                                "page_number": page_num,
                                "content": current_chunk,
                                "token_count": token_estimate
                            })
                            chunk_idx += 1
                            # Retain overlap from end of current chunk
                            overlap_text = current_chunk[-chunk_overlap:] if len(current_chunk) > chunk_overlap else ""
                            current_chunk = f"{overlap_text} {sent}".strip()
                        else:
                            # Sentence itself is huge, hard slice
                            current_chunk = sent
            else:
                if len(current_chunk) + len(para) + 2 <= chunk_size:
                    current_chunk = f"{current_chunk}\n\n{para}".strip()
                else:
                    if current_chunk:
                        token_estimate = max(1, len(current_chunk.split()))
                        chunks.append({
                            "chunk_index": chunk_idx,
                            "page_number": page_num,
                            "content": current_chunk,
                            "token_count": token_estimate
                        })
                        chunk_idx += 1
                        overlap_text = current_chunk[-chunk_overlap:] if len(current_chunk) > chunk_overlap else ""
                        current_chunk = f"{overlap_text}\n\n{para}".strip()
                    else:
                        current_chunk = para

        if current_chunk:
            token_estimate = max(1, len(current_chunk.split()))
            chunks.append({
                "chunk_index": chunk_idx,
                "page_number": page_num,
                "content": current_chunk,
                "token_count": token_estimate
            })
            chunk_idx += 1

    return chunks
