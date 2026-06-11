# CLAUDE.md — AI 文档问答工具(RAG)

> 本文件是项目级指令,Claude 在本仓库工作时必须遵守。
> 路线图见 [plan.md](./plan.md),任务清单见 [task.md](./task.md)。

## 项目是什么

一句话:**上传文档 → AI 基于文档内容回答问题,并标注答案出处。**

这是一个独立开发者的作品集 / Upwork 接单案例,核心卖点是"答案带**引用来源**",让客户一眼看出"AI 没瞎编"。MVP 范围严格受控,**不做**:多用户权限、支付、团队协作、移动端适配。

## 目录结构

```
util_rag/
├── backend/          # Python / FastAPI
│   ├── main.py           # FastAPI 入口,路由注册,/health
│   ├── ai_client.py      # ⭐ AI 抽象层(embedding + LLM),方案 A/B 切换
│   ├── ingest.py         # 文档解析 → 切块 → 向量化 → 入库
│   ├── query.py          # 检索 → 拼 Prompt → 流式问答
│   ├── db.py             # SQLModel 模型 + SQLite 连接
│   ├── vectorstore.py    # Chroma 封装
│   └── .env              # 密钥(不进 Git)
├── frontend/         # Vue 3 + Vite + Arco Design Vue
│   └── src/
├── deploy/           # Dockerfile / docker-compose.yml / Caddyfile
├── plan.md           # 路线图
└── task.md           # 任务清单(改一项就更新状态)
```

## 技术栈(已定,勿擅自更换)

| 层 | 选型 | 备注 |
|---|---|---|
| 后端框架 | FastAPI + uvicorn | |
| 文档解析 | pymupdf(PDF)、纯文本直读 | |
| 切块 | langchain-text-splitters `RecursiveCharacterTextSplitter` | chunk ~500 字 / overlap ~50 |
| 向量库 | Chroma(本地嵌入式) | 零运维,持久化到磁盘目录 |
| 数据库 | **SQLite + SQLModel** | ⚠️ 不是 MySQL,适配 1GB VPS |
| Embedding/LLM | 方案 A:OpenAI / 方案 B:智谱 GLM 或 DashScope | 经 `ai_client.py` 切换 |
| 前端 | Vue 3 + Vite | |
| UI 库 | **Arco Design Vue**(`@arco-design/web-vue`) | 按需引入 |
| 部署 | Vultr VPS(1GB)+ Docker + Caddy | Caddy 自动 HTTPS |

## 开发规则(Rules)—— 必须遵守

1. **AI 调用一律走 `ai_client.py`**。任何地方都不要直接 `import openai` 或写死某家 SDK;embedding 和 chat 都通过抽象层,靠 `.env` 的配置切换方案 A/B。这是本项目能"开发用国内、部署用海外"的命脉。
2. **答案必须可溯源**。问答接口除了返回答案,**必须同时返回命中的来源片段 + 出处**(文档名、页码/片段序号)。任何改动都不得丢掉 citation 数据——这是产品的核心卖点。
3. **Prompt 必须约束"只基于给定片段回答"**。系统提示词明确:只用检索到的上下文回答,**找不到就老实说"找不到",严禁编造**。
4. **问答走流式**。LLM 回答用流式返回(SSE 或 ReadableStream),前端逐字渲染。
5. **数据库只用 SQLite**。用 SQLModel 写,别引入 MySQL/Postgres。表:`documents` / `conversations` / `messages`。
6. **前端 UI 用 Arco,按需引入**。组件优先用 Arco 现成的:`a-upload`(拖拽+进度)、`a-list`、`a-collapse`(来源折叠)、`a-input`/`a-button`、`a-spin`/`a-empty`/`a-message`。
7. **守住 MVP 边界**。"后续延伸"(Word/URL/Excel、多知识库、多租户 SaaS、客户系统对接)一律**先不做**,除非用户明确要求。别擅自扩范围。
8. **部署受 1GB 内存约束**。VPS 上**不跑任何本地 AI 模型**(embedding/LLM 全走云端 API);改动不得引入吃内存的本地推理。
9. **密钥不进 Git**。API key、模型配置只放 `.env`;确保 `.gitignore` 覆盖 `.env`、Chroma 数据目录、上传文件目录、SQLite 文件。
10. **改完任务同步 task.md**。完成 task.md 里某项后,把它前面的 ⬜ 改成 ✅。

## 常用命令

```bash
# 后端(在 backend/)
uvicorn main:app --reload --port 8000      # 起开发服务
# 前端(在 frontend/)
pnpm dev                                    # 起开发服务
pnpm build                                  # 产出 dist/
```

> 本机已装 RTK,执行 shell 命令时按全局 CLAUDE.md 约定加 `rtk` 前缀。

## 工作协议

遵守用户全局的 RIPER 协议(RESEARCH/INNOVATE/PLAN/EXECUTE/REVIEW):每次回复开头声明模式,未经独立成行关键词指令不擅自改代码、不扩范围。
