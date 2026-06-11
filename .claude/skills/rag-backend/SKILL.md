---
name: rag-backend
description: 本项目 RAG 后端(FastAPI)的实现约定——文档入库管线、检索问答管线、AI 抽象层、来源溯源、SQLite 数据模型。当在 backend/ 写或改后端代码(上传、解析、切块、向量化、检索、Prompt、流式问答、ai_client、数据库)时使用。
---

# RAG 后端实现约定

本项目后端的统一规范。改任何后端代码前先读这里,确保与既定架构一致。详见仓库根的 [CLAUDE.md](../../../CLAUDE.md)。

## AI 抽象层 `ai_client.py`(命脉)

所有 embedding 和 chat 调用**只能**经过这一层,严禁在业务代码里直接用某家 SDK。对外暴露稳定接口:

- `embed(texts: list[str]) -> list[list[float]]` — 批量向量化
- `chat_stream(messages: list[dict]) -> Iterator[str]` — 流式对话,逐块 yield 文本

内部按 `.env` 的 `AI_PROVIDER`(`openai` / `zhipu` / `dashscope`)分发:
- **方案 A(海外/部署)**:OpenAI `text-embedding-3-small` + `gpt-4o-mini`
- **方案 B(国内/开发)**:智谱 GLM 或 DashScope(通义)的 embedding + chat

切换只改 `.env`,不改业务代码。

## 入库管线 `ingest.py`

`上传 → 解析 → 切块 → 向量化 → 入库`,顺序与参数:

1. **解析**:PDF 用 `pymupdf`(逐页提取文本,记录页码);txt/md 直接读。
2. **切块**:`RecursiveCharacterTextSplitter`,`chunk_size≈500`、`chunk_overlap≈50`。
3. **向量化**:`ai_client.embed()` 批量,别逐条调(省请求)。
4. **入库**:每个 chunk 存进 Chroma,**metadata 必须带** `{doc_id, doc_name, page 或 chunk_index}` —— 这是后面来源溯源的依据,不能省。
5. SQLite `documents` 表记一条文档元信息(id、文件名、上传时间、chunk 数)。

## 问答管线 `query.py`

`问题 → embedding → 检索 → 拼 Prompt → 流式回答 + 返回来源`:

1. 问题 `ai_client.embed()` → Chroma 检索 `top_k=4` 相关片段(连同 metadata)。
2. **系统 Prompt(铁律)**:约束模型"只依据下面提供的片段回答;若片段中没有答案,直接说『根据现有文档找不到相关内容』,**绝不编造**"。把检索片段拼进上下文。
3. `ai_client.chat_stream()` 流式产出答案。
4. **响应除了答案,必须同时回传命中片段 + 出处**(doc_name + page/chunk_index)给前端;citation 数据任何时候都不能丢。
5. 对话存 SQLite:`conversations`(会话)、`messages`(每条问/答,答附带 sources)。

## 数据库 `db.py`

SQLite + SQLModel(**不是 MySQL**)。三张表:`documents`、`conversations`、`messages`。连接用单文件,路径来自配置,部署时挂 volume 持久化。

## 流式接口

问答接口用 SSE 或 `StreamingResponse` 把答案逐块下发;来源数据可在流首部或流尾用约定事件(如 `event: sources`)随流返回,便于前端展示"📎 来源"。

## 不要做

- 不引入本地 embedding/LLM 模型(1GB VPS 跑不动,且违背抽象层设计)。
- 不扩 MVP 之外的格式/功能(Word/URL/Excel、多租户等),除非用户明确要求。
