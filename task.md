# 任务清单:AI 文档问答工具(RAG)

> 状态说明:⬜ 待办 · 🔄 进行中 · ✅ 已完成
> 任务拆解自 [plan.md](./plan.md),完成一项就把前面的 ⬜ 改成 ✅。

---

## 阶段 0:环境与骨架(0.5 天)

- ✅ 0.1 建仓库(GitHub,作品集需可展示),前后端分目录 ⚠️ 本地结构已建;GitHub 远程仓库待你的账号 push
- ✅ 0.2 后端搭 FastAPI 骨架,跑通 `/health` 接口
- ✅ 0.3 前端建 Vue3 + Vite 工程,跑通空白页
- ✅ 0.4 前端装好 Arco Design Vue(`@arco-design/web-vue`),配按需引入(`unplugin-vue-components` + Arco resolver)
- ⬜ 0.5 申请 AI API key(国内模型 + OpenAI 各一) ⚠️ 需你本人申请,填入 backend/.env
- ✅ 0.6 封装 `ai_client.py` 抽象层,把 embedding / LLM 调用包一层,方便方案 A/B 切换

---

## 阶段 1:文档入库管线(2-3 天)—— 核心

- ✅ 1.1 上传接口:接收文件 → 存到本地/对象存储 → SQLite 记一条文档记录(documents 表)
- ✅ 1.2 文档解析:pymupdf 提取 PDF 文本;txt / md 直接读
- ✅ 1.3 切块:RecursiveCharacterTextSplitter,chunk ~500 字、overlap ~50
- ✅ 1.4 向量化:每个 chunk 调 embedding → 存入 Chroma(附元信息:文档名、页码/片段序号)
- ✅ 1.5 自测:上传一个 PDF,确认 Chroma 里有向量、能检索 ✓ 已联网实测通过(zhipu embedding-3)

---

## 阶段 2:问答管线(2-3 天)—— 核心

- ✅ 2.1 提问接口:用户问题 → embedding → Chroma 检索 top-k(如 4)相关片段
- ✅ 2.2 拼 Prompt:系统提示词约束"只基于提供的片段回答,不知道就说不知道",带上检索片段
- ✅ 2.3 调 LLM,**流式**返回答案
- ✅ 2.4 同时返回"引用来源"(命中片段 + 出处)给前端
- ✅ 2.5 对话历史存 SQLite(conversations / messages 表)

---

## 阶段 3:前端界面(2-3 天)

- ✅ 3.1 上传页:`a-upload` 拖拽上传 + 上传进度 + `a-list` 已上传文档列表
- ✅ 3.2 聊天页:消息流 + 流式打字效果(`fetch` + ReadableStream 或 SSE)
- ✅ 3.3 来源展示:每条 AI 回答下方 `a-collapse` 可展开"📎 来源",显示命中片段和文档名
- ✅ 3.4 基础打磨:loading 态(`a-spin`)、空状态(`a-empty`)、错误提示(`a-message`)。界面干净即可

---

## 阶段 4:部署与包装(1-2 天)—— 决定能不能变现

> 目标环境:已有的 Vultr VPS(1GB 内存,当前在跑 VPN),两者共存互不干扰。
> ⚠️ 域名当前等 Visa 信用卡下来后再买,4.0 / 4.5 暂挂起;其余可先做。

- ⬜ 4.0 前置:买域名(Cloudflare/Namecheap)+ 加 A 记录指向 Vultr IP;放行 80 / 443 端口 ⏸️(等卡)
- ⬜ 4.1 给 VPS 加 2GB Swap → 启用 → 写入 `/etc/fstab` 持久化(必做)
- ⬜ 4.2 VPS 装 Docker + Docker Compose
- ⬜ 4.3 后端 Docker 化:写 `Dockerfile`;SQLite / Chroma / 上传目录用 volume 挂到宿主机
- ⬜ 4.4 前端 `vite build` 产出 `dist/` 静态文件
- ⬜ 4.5 写 `Caddyfile`:根路径服务前端 dist,`/api/*` 反代后端,Caddy 自动 HTTPS ⏸️(依赖域名)
- ⬜ 4.6 写 `docker-compose.yml`(backend + caddy),`docker compose up -d` 启动
- ⬜ 4.7 配 `.env`:AI API key、模型选择(方案 A/B);`.env` 不进 Git
- ⬜ 4.8 上线验证:浏览器开站点确认上传+问答+HTTPS 正常;`docker compose logs` 排错;`free -h` 看内存/swap
- ⬜ 4.9 准备演示用文档(产品手册/政策文件),预设几个漂亮问答
- ⬜ 4.10 录 1-2 分钟演示视频(屏幕录制 + AI 生成英文字幕/旁白)
- ⬜ 4.11 写 README:项目介绍、技术栈、在线 demo 链接、截图

---

## 阶段 5:转化为 Upwork 案例(0.5 天)

- ⬜ 5.1 Upwork 简介定位:"I build AI knowledge-base assistants & document Q&A systems for your business"(卖解决方案)
- ⬜ 5.2 把 demo 做成 Portfolio item:标题 + 演示视频 + 在线链接 + 一句话价值
- ⬜ 5.3 Project Catalog 拆 3 档:基础问答 / 带知识库管理 / 接入现有系统,标好价和交付周期

---

## 里程碑验证

- ✅ M1 技术验证:上传陌生 PDF,问里面的问题答得对且给出正确来源;问文档没有的内容老实说"找不到" ✓ 2026-06-12 实测:有答案题答对带来源;无答案题回"根据现有文档找不到相关内容"不瞎编
- ⬜ M2 作品验证:陌生人点开 demo,30 秒内能自己上传文档并问出答案
- ⬜ M3 商业验证:Upwork 上线后 3 个月内至少接到 1 单相关咨询/订单
