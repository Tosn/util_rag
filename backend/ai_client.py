"""AI 抽象层(命脉)—— 全项目唯一允许直接使用 AI SDK 的地方。

embedding 与 chat 一律经此层,业务代码不得直接 import openai 或写死某家 SDK。
三家(openai / zhipu / dashscope)均提供 OpenAI 兼容端点,故用 openai SDK 作统一传输,
仅靠 config 切换 base_url / api_key / 模型名。切换方案只改 .env,不动业务代码。
"""
from __future__ import annotations

from collections.abc import Iterator

from openai import OpenAI

from config import settings

_client: OpenAI | None = None


def _get_client() -> OpenAI:
    """惰性构造当前 provider 的 OpenAI 兼容客户端。"""
    global _client
    if _client is None:
        if not settings.active_api_key:
            raise RuntimeError(
                f"未配置 {settings.ai_provider} 的 API key,请在 backend/.env 中填写。"
            )
        _client = OpenAI(
            api_key=settings.active_api_key,
            base_url=settings.active_base_url,
        )
    return _client


def embed(texts: list[str]) -> list[list[float]]:
    """批量向量化。输入文本列表,返回等长的向量列表。"""
    if not texts:
        return []
    resp = _get_client().embeddings.create(
        model=settings.active_embedding_model,
        input=texts,
    )
    # 按 index 排序确保与输入顺序一致
    items = sorted(resp.data, key=lambda d: d.index)
    return [item.embedding for item in items]


def chat_stream(messages: list[dict]) -> Iterator[str]:
    """流式对话。逐块 yield 文本增量(已剔除空块)。"""
    stream = _get_client().chat.completions.create(
        model=settings.active_chat_model,
        messages=messages,
        stream=True,
    )
    for chunk in stream:
        if not chunk.choices:
            continue
        delta = chunk.choices[0].delta
        content = getattr(delta, "content", None)
        if content:
            yield content
