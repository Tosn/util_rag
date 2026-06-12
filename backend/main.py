"""FastAPI 入口:路由注册、CORS、启动建表。

接口:
  GET  /health                 健康检查
  POST /api/documents          上传并入库一份文档
  GET  /api/documents          已入库文档列表
  POST /api/chat               基于文档的流式问答(SSE),流尾回传来源
"""
from __future__ import annotations

import json
import shutil
import uuid
from collections.abc import Iterator

from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlmodel import Session, select

import ingest
import query
from config import settings
from db import Conversation, Document, Message, get_session, init_db, new_session

app = FastAPI(title="AI 文档问答工具 (RAG)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 允许上传的扩展名
_ALLOWED_EXT = (".pdf", ".txt", ".md", ".markdown")


@app.on_event("startup")
def _on_startup() -> None:
    init_db()


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "provider": settings.ai_provider}


@app.post("/api/documents")
async def upload_document(
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
) -> dict:
    filename = file.filename or "untitled"
    if not filename.lower().endswith(_ALLOWED_EXT):
        raise HTTPException(400, detail="仅支持 PDF / TXT / Markdown 文件")

    # 存盘:用 uuid 前缀避免重名覆盖
    settings.ensure_dirs()
    safe_name = f"{uuid.uuid4().hex}_{filename}"
    dest = settings.upload_dir / safe_name
    with dest.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    size = dest.stat().st_size

    try:
        doc = ingest.ingest_document(
            session=session,
            path=str(dest),
            filename=filename,
            content_type=file.content_type or "",
            size=size,
        )
    except Exception as exc:  # 入库失败:删盘并上报
        dest.unlink(missing_ok=True)
        raise HTTPException(500, detail=f"文档入库失败:{exc}") from exc

    return {
        "id": doc.id,
        "filename": doc.filename,
        "size": doc.size,
        "chunk_count": doc.chunk_count,
        "created_at": doc.created_at.isoformat(),
    }


@app.get("/api/documents")
def list_documents(session: Session = Depends(get_session)) -> list[dict]:
    docs = session.exec(select(Document).order_by(Document.created_at.desc())).all()
    return [
        {
            "id": d.id,
            "filename": d.filename,
            "size": d.size,
            "chunk_count": d.chunk_count,
            "created_at": d.created_at.isoformat(),
        }
        for d in docs
    ]


class ChatRequest(BaseModel):
    question: str
    conversation_id: int | None = None


def _sse(event: str, data: object) -> str:
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


@app.post("/api/chat")
def chat(req: ChatRequest, session: Session = Depends(get_session)) -> StreamingResponse:
    question = req.question.strip()
    if not question:
        raise HTTPException(400, detail="问题不能为空")

    # 1) 检索 + 组织来源(在进入流之前完成,便于异常直接返回)
    hits = query.retrieve(question)
    sources = query.build_sources(hits)

    # 2) 会话:沿用或新建
    conversation_id = req.conversation_id
    if conversation_id is None:
        conv = Conversation(title=question[:40])
        session.add(conv)
        session.commit()
        session.refresh(conv)
        conversation_id = conv.id
    # 存用户消息
    session.add(Message(conversation_id=conversation_id, role="user", content=question))
    session.commit()

    def event_stream() -> Iterator[str]:
        # 先告知前端会话 id
        yield _sse("meta", {"conversation_id": conversation_id})
        parts: list[str] = []
        try:
            for token in query.answer_stream(question, hits):
                parts.append(token)
                yield _sse("token", {"text": token})
        except Exception as exc:  # noqa: BLE001
            yield _sse("error", {"message": f"生成回答失败:{exc}"})
            return
        answer = "".join(parts)
        # 持久化 assistant 消息(含来源)。请求级 session 此时已关闭,另开独立 session。
        with new_session() as s2:
            s2.add(
                Message(
                    conversation_id=conversation_id,
                    role="assistant",
                    content=answer,
                    sources_json=json.dumps(sources, ensure_ascii=False),
                )
            )
            s2.commit()
        # 流尾回传来源 + 结束标记
        yield _sse("sources", sources)
        yield _sse("done", {"conversation_id": conversation_id})

    return StreamingResponse(event_stream(), media_type="text/event-stream")
