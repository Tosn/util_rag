# Backend — AI 文档问答工具(RAG)

基于 FastAPI 的 RAG 后端:**上传文档 → 解析切块 → 向量化入库 → 检索 → 流式问答,并回传答案出处**。

答案严格基于检索到的文档片段,找不到就如实说「根据现有文档找不到相关内容」,绝不编造;每条回答附带命中片段 + 出处(文档名、页码/片段序号)。

## 技术栈

| 层 | 选型 |
|---|---|
| Web 框架 | FastAPI + uvicorn |
| 文档解析 | pymupdf(PDF,逐页带页码)/ 纯文本直读(txt、md) |
| 切块 | langchain-text-splitters `RecursiveCharacterTextSplitter`(chunk≈500 / overlap≈50) |
| 向量库 | Chroma(本地持久化,零运维) |
| 数据库 | SQLite + SQLModel(三表:documents / conversations / messages) |
| Embedding & LLM | 经 `ai_client.py` 抽象层,`.env` 切换:智谱 GLM / OpenAI / 阿里 DashScope |

## 目录结构

```
backend/
├── main.py          # FastAPI 入口、路由、CORS、/health
├── config.py        # 配置(从 .env 读,集中管理路径/方案/检索参数)
├── ai_client.py     # ⭐ AI 抽象层(embed + chat_stream),方案 A/B 切换的命脉
├── ingest.py        # 入库管线:解析 → 切块 → 向量化 → 入 Chroma + SQLite
├── query.py         # 问答管线:检索 → 拼 Prompt → 流式回答 + 来源
├── db.py            # SQLModel 模型 + SQLite 连接
├── vectorstore.py   # Chroma 封装
├── requirements.txt
├── .env.example     # 配置模板(拷成 .env 填 key)
└── data/            # 运行期生成(SQLite / Chroma / uploads),已 gitignore
```

## 安装

```bash
cd backend
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

## 配置

把 `.env.example` 拷为 `.env` 并填入 API key(`.env` 不进 Git):

```bash
cp .env.example .env
```

```ini
# 当前方案:openai / zhipu / dashscope
AI_PROVIDER=zhipu
# 开发默认用智谱(国内访问稳定),从 https://open.bigmodel.cn/ 获取
ZHIPU_API_KEY=你的key
# 部署 demo 切海外方案 A 时填:
OPENAI_API_KEY=
```

> 切换方案只改 `.env`、不动业务代码。默认模型:智谱 `embedding-3` + `glm-4-flash`。

## 启动

```bash
.venv/bin/uvicorn main:app --reload --port 8000
```

> ⚠️ 若 8000 端口被占用,可换端口(如 `--port 8010`),并同步改 `frontend/vite.config.js` 里的 proxy target。

## API

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/health` | 健康检查,返回当前 provider |
| POST | `/api/documents` | 上传并入库一份文档(form-data `file`,支持 PDF/TXT/MD) |
| GET | `/api/documents` | 已入库文档列表 |
| POST | `/api/chat` | 基于文档的流式问答(SSE),流尾回传来源 |

**`/api/chat` 的 SSE 事件**:`meta`(会话 id)→ 多个 `token`(答案增量)→ `sources`(命中来源)→ `done`;出错时为 `error`。

## 约束

- 所有 AI 调用一律走 `ai_client.py`,不在业务代码直接 import 某家 SDK。
- 答案必须可溯源,citation 数据任何改动都不能丢。
- 只用 SQLite(不引入 MySQL/Postgres)。
- 不跑任何本地 embedding/LLM 模型(适配 1GB VPS,全走云端 API)。
