# 实施计划:AI 文档问答工具(RAG)—— 独立开发者作品集 / Upwork 接单案例

## Context(为什么做这个)

背景:40+ 前端/全栈程序员提前规划职业第二曲线。已确定路线 = **海外私单(Upwork)+ AI 赋能**。
- 财务:无房贷、2 娃、1 年备用金 → 有容错空间,但只能稳不能赌。
- 技术栈:Vue 熟、Python/MySQL 会一些,AI 辅助下可独立全栈。
- 英语不好,但接单沟通以文字为主,AI 翻译可补齐。

目标:在**在职阶段**用业余时间做出 1 个"AI 赋能"的工具类作品。它一物三用:
1. 学会当下最值钱的技能 —— **RAG / AI 集成**;
2. 成为 Upwork 上有说服力的案例(撬动"企业知识库 / AI 客服 / 内部助手"一整类订单);
3. 未来可产品化成 SaaS 或"睡后收入"。

最终交付物 = 一个能跑的 Demo(线上可访问)+ 1-2 分钟演示视频 + Upwork 服务页文案。

---

## 产品形态(MVP 范围)

一句话:**上传文档 → AI 基于文档内容回答问题,并标注答案出处。**

必须有(MVP):
- 上传 PDF / TXT / Markdown 文档
- 文档解析 → 切块 → 向量化 → 入库
- 聊天式提问,流式返回答案
- 答案下方展示**引用来源片段**(专业感关键,客户一眼看懂"它没瞎编")

先不做(避免范围蔓延):多用户权限体系、支付、复杂团队协作、移动端适配。

---

## 技术选型(都用轻量、好上手的)

**后端(Python / FastAPI)**
- Web 框架:`FastAPI` + `uvicorn`
- 文档解析:`pymupdf`(PDF,效果好)、纯文本直接读
- 切块:用 `langchain-text-splitters` 的 RecursiveCharacterTextSplitter(或自己写,按段落+字数)
- 向量库:`Chroma`(本地嵌入式,零运维,最适合 demo)
- Embedding & LLM:见下方"AI 服务"二选一
- 数据库:`SQLite`(存文档元信息、对话历史)——单文件、零常驻进程、零常驻内存,最适配 1GB VPS;用 `SQLModel`(基于 SQLAlchemy)做 ORM
  - 备注:本想用 MySQL 展示你已有技能,但本项目 DB 只存"文档元信息 + 对话历史"这点数据,SQLite 完全够用且部署省内存;ORM 写法与 MySQL 几乎一致,日后真要上量可平滑迁回 MySQL

**AI 服务(关键决策:国内访问 vs 海外演示)**
- 方案 A(推荐,面向海外客户):OpenAI `text-embedding-3-small`(便宜)+ `gpt-4o-mini`(便宜快)。需解决国内网络访问(代理 / 中转 API)。
- 方案 B(国内访问稳定):智谱 GLM 或阿里 DashScope(通义)的 embedding + chat 模型,接口类似。
- 建议:**开发用 B 保证顺畅,部署 demo 时切到 A**,代码里把 AI 调用封装成一层,方便切换。

**前端(Vue 3)**
- `Vue 3 + Vite`
- UI:`Arco Design Vue`(字节出品,组件全、设计现代专业,作品集加分;开箱即用的拖拽上传、消息气泡、折叠面板等正好覆盖本项目交互)
  - 安装:`@arco-design/web-vue`,按需引入(配 `unplugin-vue-components` + `@arco-design/web-vue/resolver`)减小体积
  - 主要用到的组件:`a-upload`(拖拽上传 + 进度)、`a-list`(文档列表)、`a-collapse`(来源片段折叠)、`a-input` / `a-button`(提问框)、`a-spin` / `a-empty` / `a-message`(loading/空态/错误提示)
- 关键交互:文档上传(拖拽)、流式聊天界面、来源片段折叠展示
- 流式输出:用 `fetch` + `ReadableStream` 或 SSE 接收后端 stream

**部署(让客户能点开链接)**
- 后端:Railway / Render / Fly.io(有免费额度,部署 Python 简单)
- 前端:Vercel / Netlify(免费)
- 或买个便宜 VPS 用 Docker 一把梭

---

## 分阶段执行清单

### 阶段 0:环境与骨架(0.5 天)
1. 建仓库(GitHub,作品集要公开或可展示),前后端分目录。
2. 后端建 FastAPI 骨架,跑通 `/health` 接口。
3. 前端建 Vue3+Vite 工程,跑通空白页。
4. 申请好 AI API key(国内模型 + OpenAI 各一),封装 `ai_client.py` 抽象层。

### 阶段 1:文档入库管线(2-3 天)—— 核心
5. 上传接口:接收文件 → 存到本地/对象存储 → SQLite 记一条文档记录(documents 表)。
6. 解析:pymupdf 提取文本(PDF),txt/md 直接读。
7. 切块:RecursiveCharacterTextSplitter,chunk ~500 字、overlap ~50。
8. 向量化:每个 chunk 调 embedding → 存入 Chroma(附带元信息:文档名、页码/片段序号)。
9. 自测:上传一个 PDF,确认 Chroma 里有向量、能检索。

### 阶段 2:问答管线(2-3 天)—— 核心
10. 提问接口:用户问题 → embedding → Chroma 检索 top-k(如 4)相关片段。
11. 拼 Prompt:系统提示词约束"只基于提供的片段回答,不知道就说不知道",带上检索到的片段。
12. 调 LLM,**流式**返回答案。
13. 同时返回"引用来源"(命中的片段 + 出处)给前端。
14. 对话历史存 SQLite(conversations / messages 表)。

### 阶段 3:前端界面(2-3 天)
15. 上传页:拖拽上传 + 上传进度 + 已上传文档列表。
16. 聊天页:消息流 + 流式打字效果。
17. 来源展示:每条 AI 回答下方可展开"📎 来源",显示命中片段和文档名。
18. 基础打磨:loading 态、空状态、错误提示。界面干净即可,不求花哨。

### 阶段 4:部署与包装(1-2 天)—— 决定能不能变现

> 部署目标环境:**已有的 Vultr VPS(1GB 内存,当前在跑 VPN)**。VPN 与本应用共存、互不干扰(VPN 占网络转发,应用占 Web 端口)。AI(embedding/LLM)全走云端 API,VPS 上不跑任何本地模型,故 1GB 可行。

19. 部署后端 + 前端到 Vultr,拿到可访问的公开链接。按以下子步骤执行:
    - **19.0 前置**:在 Cloudflare 或 Namecheap 买域名 → 加一条 A 记录指向 Vultr 的公网 IP;在 Vultr 面板 / VPS 防火墙放行 `80`、`443` 端口(VPN 端口保持不动)。
    - **19.1 加 2GB Swap(必做)**:在 VPS 上创建 2GB swap 文件 → 启用 → 写入 `/etc/fstab` 持久化。给 1GB 机器加内存缓冲垫,防止内存瞬时冲高把服务挤崩。
    - **19.2 装 Docker + Docker Compose**:作为统一运行环境,避免在宿主机直接装一堆 Python/系统依赖。
    - **19.3 后端 Docker 化**:为 FastAPI 写 `Dockerfile`;把 SQLite 文件、Chroma 持久化目录、上传文件目录用 volume 挂到宿主机,容器重建时数据不丢。
    - **19.4 前端构建**:本地或 VPS 上 `vite build` 产出 `dist/` 静态文件,交给 Caddy 托管(前端不单独起容器)。
    - **19.5 Caddy 反向代理 + 自动 HTTPS**:写 `Caddyfile`,一个域名块完成——根路径服务前端 `dist/`,`/api/*` 反代到后端容器;Caddy 自动申请并续期 Let's Encrypt 证书(省掉 Nginx + Certbot 的手动活)。
    - **19.6 编排**:写 `docker-compose.yml`,服务为 `backend` + `caddy`(SQLite/Chroma 是文件,无需独立服务);`docker compose up -d` 一键启动。
    - **19.7 环境变量与密钥**:`.env` 存 AI API key、模型选择(对应技术选型里方案 A/B 的切换);`.env` 不进 Git。
    - **19.8 验证上线**:浏览器开 `https://你的域名`,确认能上传 + 问答、HTTPS 锁标志正常;`docker compose logs` 排错;`free -h` 看内存/swap 占用是否健康。
20. 准备一份**演示用文档**(比如一份产品手册 / 政策文件),预设几个漂亮的问答。
21. 录 1-2 分钟演示视频(屏幕录制 + AI 生成英文字幕/旁白)。
22. 写 README:项目介绍、技术栈、在线 demo 链接、截图。

### 阶段 5:转化为 Upwork 案例(0.5 天)
23. Upwork 简介定位:**"I build AI knowledge-base assistants & document Q&A systems for your business"**(卖解决方案,不堆技术名词)。
24. 把这个 demo 作为 Portfolio item:标题 + 演示视频 + 在线链接 + 一句话价值("Turn your documents into an AI assistant with cited answers")。
25. 服务包(Project Catalog)拆 3 档:基础问答 / 带知识库管理 / 接入现有系统,标好价和交付周期。

---

## 时间预估

- 总工时 ~10-14 个工作日 → 按业余每天 2-3 小时,**3-4 周出可演示成品**。
- 不要追求完美,阶段 0-2 跑通就已经是"能演示的核心";阶段 3-5 是把它变成"能卖的东西"。

---

## 验证方式(怎么算成功)

1. **技术验证**:上传一份从没训练过的 PDF,问里面的具体问题,AI 答得对且能给出正确来源片段;问文档里没有的内容,AI 老实说"找不到"(不瞎编)。
2. **作品验证**:陌生人点开 demo 链接,30 秒内能自己上传文档并问出答案。
3. **商业验证(真正目标)**:Upwork 上线后,3 个月内**至少接到 1 单**相关咨询/订单——哪怕 50 美金,也验证了"脱离公司平台能独立赚到外汇"。

---

## 后续延伸(MVP 跑通后再说,别提前做)

- 支持更多格式(Word、网页 URL、Excel)
- 多文档/知识库管理、文档分组
- 接入客户现有系统(API / 网站插件 / 企微/飞书机器人)—— 这是**单价最高**的延伸方向
- 做成多租户 SaaS,加订阅付费

---

## 备注

- 这是用户的**个人独立项目**,不在当前 taxssp 工作仓库内执行;本文件是一份可照着做的路线图,由用户本人分阶段实施。
- 所有对外文案(Upwork 简介、邮件、视频字幕)用 AI 做英文翻译+润色,弥补英语短板。
