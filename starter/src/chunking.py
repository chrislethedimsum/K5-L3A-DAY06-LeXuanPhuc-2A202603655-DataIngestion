"""Implement fixed-size and structure-aware chunking."""
from .models import Chunk, DocumentPage
import re


def fixed_size(page: DocumentPage, size: int = 500, overlap: int = 50) -> list[Chunk]:
    """Chiến lược A: Cắt sliding window kích thước cố định theo ký tự."""
    text = page.text
    chunks: list[Chunk] = []
    start = 0
    idx = 1
    while start < len(text):
        end = min(start + size, len(text))
        sub_text = text[start:end].strip()
        if sub_text:
            cid = f"A_{page.document_id}_p{page.page}_c{idx}"
            chunks.append(
                Chunk(
                    chunk_id=cid,
                    document_id=page.document_id,
                    source=page.source,
                    page=page.page,
                    text=sub_text,
                    metadata=dict(page.metadata)
                )
            )
            idx += 1
        if end >= len(text):
            break
        start += (size - overlap)
    return chunks


def by_paragraph(page: DocumentPage, max_size: int = 800) -> list[Chunk]:
    """Chiến lược B & C: Tách theo ranh giới tự nhiên (Khoản 1., 2., Điểm a), b), Điều)."""
    # Regex tách theo các mốc điểm/khoản của văn bản luật
    segments = re.split(r'(?=\b\d+\.\s+|\b[a-đ]\)\s+|“?Điều\s+\d+)', page.text)
    segments = [s.strip() for s in segments if s.strip()]
    if not segments:
        segments = [page.text]
    chunks: list[Chunk] = []
    buffer: list[str] = []
    current_len = 0
    idx = 1
    for seg in segments:
        # Nếu 1 khoản dài hơn max_size thì lưu buffer cũ rồi cắt nhỏ khoản đó
        if len(seg) > max_size:
            if buffer:
                c_text = " ".join(buffer).strip()
                chunks.append(
                    Chunk(
                        chunk_id=f"B_{page.document_id}_p{page.page}_c{idx}",
                        document_id=page.document_id,
                        source=page.source,
                        page=page.page,
                        text=c_text,
                        metadata=dict(page.metadata)
                    )
                )
                idx += 1
                buffer = []
                current_len = 0
            sub_start = 0
            while sub_start < len(seg):
                sub_end = min(sub_start + max_size, len(seg))
                chunks.append(
                    Chunk(
                        chunk_id=f"B_{page.document_id}_p{page.page}_c{idx}",
                        document_id=page.document_id,
                        source=page.source,
                        page=page.page,
                        text=seg[sub_start:sub_end].strip(),
                        metadata=dict(page.metadata)
                    )
                )
                idx += 1
                sub_start += max_size
            continue
        if current_len + len(seg) + 1 <= max_size:
            buffer.append(seg)
            current_len += len(seg) + 1
        else:
            c_text = " ".join(buffer).strip()
            chunks.append(
                Chunk(
                    chunk_id=f"B_{page.document_id}_p{page.page}_c{idx}",
                    document_id=page.document_id,
                    source=page.source,
                    page=page.page,
                    text=c_text,
                    metadata=dict(page.metadata)
                )
            )
            idx += 1
            buffer = [seg]
            current_len = len(seg)
    if buffer:
        c_text = " ".join(buffer).strip()
        chunks.append(
            Chunk(
                chunk_id=f"B_{page.document_id}_p{page.page}_c{idx}",
                document_id=page.document_id,
                source=page.source,
                page=page.page,
                text=c_text,
                metadata=dict(page.metadata)
            )
        )
    return chunks