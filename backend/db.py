"""SQLite + SQLModel 数据层。三张表:documents / conversations / messages。

只用 SQLite(不是 MySQL),单文件零常驻,适配 1GB VPS。
"""
from __future__ import annotations

from collections.abc import Iterator
from datetime import datetime, timezone

from sqlmodel import Field, Session, SQLModel, create_engine

from config import settings


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Document(SQLModel, table=True):
    """已入库文档的元信息。"""

    id: int | None = Field(default=None, primary_key=True)
    filename: str
    content_type: str = ""
    size: int = 0
    chunk_count: int = 0
    created_at: datetime = Field(default_factory=_utcnow)


class Conversation(SQLModel, table=True):
    """一次会话。"""

    id: int | None = Field(default=None, primary_key=True)
    title: str = ""
    created_at: datetime = Field(default_factory=_utcnow)


class Message(SQLModel, table=True):
    """会话中的一条消息。assistant 消息的 sources_json 存命中来源(JSON 字符串)。"""

    id: int | None = Field(default=None, primary_key=True)
    conversation_id: int = Field(foreign_key="conversation.id", index=True)
    role: str  # "user" | "assistant"
    content: str
    sources_json: str = ""  # 仅 assistant 消息使用,存 list[Source] 的 JSON
    created_at: datetime = Field(default_factory=_utcnow)


# SQLite 引擎:同一连接可能跨线程(StreamingResponse),关闭线程检查
_engine = create_engine(
    f"sqlite:///{settings.sqlite_path}",
    connect_args={"check_same_thread": False},
)


def init_db() -> None:
    settings.ensure_dirs()
    SQLModel.metadata.create_all(_engine)


def get_session() -> Iterator[Session]:
    with Session(_engine) as session:
        yield session


def new_session() -> Session:
    """开一个独立 Session(供流式生成器在请求结束后写库使用,需自行 with 管理)。"""
    return Session(_engine)
