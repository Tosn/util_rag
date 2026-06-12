"""Chroma 向量库封装(本地持久化嵌入式)。

向量由 ai_client 在外部算好后传入,collection 不挂自带 embedding_function。
metadata 必须带 {doc_id, doc_name, page, chunk_index} —— 来源溯源的依据。
"""
from __future__ import annotations

from typing import Any

import chromadb

from config import settings

_COLLECTION_NAME = "documents"
_client: chromadb.api.ClientAPI | None = None


def _get_collection():
    global _client
    if _client is None:
        _client = chromadb.PersistentClient(path=str(settings.chroma_path))
    return _client.get_or_create_collection(
        name=_COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )


def add_chunks(
    ids: list[str],
    embeddings: list[list[float]],
    documents: list[str],
    metadatas: list[dict[str, Any]],
) -> None:
    """批量写入切块向量。"""
    if not ids:
        return
    _get_collection().add(
        ids=ids,
        embeddings=embeddings,
        documents=documents,
        metadatas=metadatas,
    )


def query(embedding: list[float], top_k: int) -> list[dict[str, Any]]:
    """按查询向量检索 top_k,返回 [{text, metadata, distance}]。"""
    res = _get_collection().query(
        query_embeddings=[embedding],
        n_results=top_k,
    )
    docs = (res.get("documents") or [[]])[0]
    metas = (res.get("metadatas") or [[]])[0]
    dists = (res.get("distances") or [[]])[0]
    hits: list[dict[str, Any]] = []
    for text, meta, dist in zip(docs, metas, dists):
        hits.append({"text": text, "metadata": meta or {}, "distance": dist})
    return hits


def delete_by_doc(doc_id: int) -> None:
    """删除某文档的所有切块(供文档删除时使用)。"""
    _get_collection().delete(where={"doc_id": doc_id})
