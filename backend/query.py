"""问答管线:问题 → embedding → 检索 → 拼 Prompt → 流式回答 + 返回来源。

系统 Prompt 铁律:只依据提供的片段回答;片段中没有答案就直说"根据现有文档找不到
相关内容",绝不编造。响应除答案外必须回传命中片段 + 出处(citation 不能丢)。
"""
from __future__ import annotations

from collections.abc import Iterator
from typing import Any

import ai_client
import vectorstore
from config import settings

_SYSTEM_PROMPT = (
    "你是一个严谨的文档问答助手。你只能依据下面【参考片段】中的内容回答用户问题。\n"
    "规则:\n"
    "1. 只用参考片段里的信息作答,不要使用任何片段之外的知识,也不要编造。\n"
    "2. 如果参考片段中找不到能回答问题的信息,直接回答:"
    "「根据现有文档找不到相关内容」,不要强行作答。\n"
    "3. 回答使用与用户提问相同的语言,简洁准确。\n"
)


def _build_context(hits: list[dict[str, Any]]) -> str:
    blocks: list[str] = []
    for i, hit in enumerate(hits, 1):
        meta = hit["metadata"]
        loc = meta.get("doc_name", "未知文档")
        if meta.get("page") is not None:
            loc += f" 第 {meta['page']} 页"
        else:
            loc += f" 片段 {meta.get('chunk_index', '?')}"
        blocks.append(f"[片段 {i}|来源:{loc}]\n{hit['text']}")
    return "\n\n".join(blocks)


def retrieve(question: str) -> list[dict[str, Any]]:
    """对问题做检索,返回 top_k 命中片段(含 metadata)。"""
    q_vec = ai_client.embed([question])[0]
    return vectorstore.query(q_vec, settings.top_k)


def build_sources(hits: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """把命中片段整理成回传前端的来源结构。"""
    sources: list[dict[str, Any]] = []
    for hit in hits:
        meta = hit["metadata"]
        sources.append(
            {
                "doc_name": meta.get("doc_name", ""),
                "page": meta.get("page"),
                "chunk_index": meta.get("chunk_index"),
                "snippet": hit["text"],
            }
        )
    return sources


def answer_stream(question: str, hits: list[dict[str, Any]]) -> Iterator[str]:
    """基于检索片段流式生成答案。"""
    context = _build_context(hits)
    messages = [
        {"role": "system", "content": _SYSTEM_PROMPT},
        {
            "role": "user",
            "content": f"【参考片段】\n{context}\n\n【问题】\n{question}",
        },
    ]
    yield from ai_client.chat_stream(messages)
