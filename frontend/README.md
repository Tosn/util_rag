# Frontend — AI 文档问答工具(RAG)

Vue 3 + Vite + Arco Design Vue 的前端:**拖拽上传文档 → 聊天式提问 → 流式逐字渲染答案 → 展开查看答案出处**。

## 技术栈

| 层 | 选型 |
|---|---|
| 框架 | Vue 3(`<script setup>`)+ Vite |
| UI 库 | Arco Design Vue(`@arco-design/web-vue`),**按需引入**(`unplugin-vue-components` + `ArcoResolver`) |
| 流式接收 | `fetch` + `ReadableStream` 解析后端 SSE |
| 上传进度 | `XMLHttpRequest`(拿 upload 进度) |

## 目录结构

```
frontend/
├── vite.config.js          # Arco 按需引入 + /api 代理到后端
└── src/
    ├── main.js
    ├── App.vue             # 两栏布局:左侧上传/文档列表,右侧聊天
    ├── api/client.js       # 文档列表 / 上传(带进度) / 流式问答(SSE 解析)
    └── components/
        ├── DocumentUpload.vue   # a-upload 拖拽上传 + 进度
        ├── DocumentList.vue     # a-list 文档列表 + a-empty 空态
        ├── ChatPanel.vue        # 消息流 + 输入框 + 发送
        ├── MessageBubble.vue    # 单条消息,流式逐字 + 光标
        └── SourceCollapse.vue   # a-collapse 「📎 来源」折叠展示
```

## 安装

```bash
cd frontend
pnpm install
```

> 本机若没有 pnpm:`npm i -g pnpm`(corepack 启用失败时用 `--force` 覆盖)。

## 启动(开发)

```bash
pnpm dev      # 打开 http://localhost:5173
```

Vite 已配 `/api` 代理到后端 `http://localhost:8000`,**需先启动后端**(见 `../backend/README.md`)。若后端换了端口,改 `vite.config.js` 里的 `proxy.target`。

## 构建(生产)

```bash
pnpm build    # 产出 dist/,部署时交给 Caddy 等静态服务托管
pnpm preview  # 本地预览构建产物
```

## 交互说明

- 左侧拖拽上传 PDF/TXT/Markdown,带进度;上传成功后文档列表自动刷新。
- 右侧输入问题(回车或点发送),答案流式逐字渲染。
- 每条 AI 回答下方可展开「📎 来源」,查看命中片段与文档名/页码。
- 加载用 `a-spin`、空态用 `a-empty`、错误提示用 `a-message`。
