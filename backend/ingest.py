"""文档入库管线:上传 → 解析 → 切块 → 向量化 → 入库。

解析:PDF 用 pymupdf 逐页提取(记录页码);txt/md 直接读。
切块:RecursiveCharacterTextSplitter,chunk≈500 / overlap≈50。
向量化:ai_client.embed 批量。
入库:Chroma(metadata 带 doc_id/doc_name/page/chunk_index)+ SQLite documents 行。
"""
from __future__ import annotations

import fitz  # pymupdf
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sqlmodel import Session

import ai_client
import vectorstore
from config import settings
from db import Document

_splitter = RecursiveCharacterTextSplitter(
    chunk_size=settings.chunk_size,
    chunk_overlap=settings.chunk_overlap,
)


def _parse(path: str, content_type: str, filename: str) -> list[tuple[str, int | None]]:
    """返回 [(文本, 页码)]。PDF 逐页带页码(从 1 起);txt/md 整篇,页码 None。"""
    lower = filename.lower()
    if lower.endswith(".pdf") or content_type == "application/pdf":
        pages: list[tuple[str, int | None]] = []
        with fitz.open(path) as doc:
            for i, page in enumerate(doc):
                text = page.get_text("text").strip()
                if text:
                    pages.append((text, i + 1))
        return pages
    # txt / md 等纯文本
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return [(f.read(), None)]


def ingest_document(
    session: Session,
    path: str,
    filename: str,
    content_type: str,
    size: int,
) -> Document:
    """解析并入库一份文档,返回已落库的 Document(含 chunk_count)。"""
    # 1) 先写 Document 行拿到 doc_id
    doc = Document(filename=filename, content_type=content_type, size=size)
    session.add(doc)
    session.commit()
    session.refresh(doc)

    # 2) 解析 → 切块,保留页码与片段序号
    pages = _parse(path, content_type, filename)
    chunk_texts: list[str] = []
    metadatas: list[dict] = []
    ids: list[str] = []
    chunk_index = 0
    for text, page in pages:
        for piece in _splitter.split_text(text):
            piece = piece.strip()
            if not piece:
                continue
            meta = {
                "doc_id": doc.id,
                "doc_name": filename,
                "chunk_index": chunk_index,
            }
            # page 可能为 None(纯文本),Chroma metadata 不接受 None,故仅在有值时写入
            if page is not None:
                meta["page"] = page
            chunk_texts.append(piece)
            metadatas.append(meta)
            ids.append(f"{doc.id}-{chunk_index}")
            chunk_index += 1

    # 3) 批量向量化 + 入 Chroma
    if chunk_texts:
        embeddings = ai_client.embed(chunk_texts)
        vectorstore.add_chunks(ids, embeddings, chunk_texts, metadatas)

    # 4) 回写 chunk_count
    doc.chunk_count = len(chunk_texts)
    session.add(doc)
    session.commit()
    session.refresh(doc)
    return doc
