---
name: arco-frontend
description: 本项目前端(Vue 3 + Vite + Arco Design Vue)的实现约定——按需引入配置、组件选型映射、拖拽上传、流式聊天渲染、来源片段折叠展示。当在 frontend/ 写或改前端界面、上传页、聊天页、来源展示时使用。
---

# 前端实现约定(Vue 3 + Arco Design Vue)

本项目前端规范。改前端前先读这里。详见仓库根的 [CLAUDE.md](../../../CLAUDE.md)。

## 技术栈与按需引入

`Vue 3 + Vite + @arco-design/web-vue`。**按需引入**减小体积:`vite.config` 里配 `unplugin-vue-components` + `@arco-design/web-vue/resolver`,组件直接用 `<a-xxx>` 不手动 import。

## 组件选型映射(优先用 Arco 现成的,别自己造轮子)

| 场景 | 用 Arco 组件 |
|---|---|
| 拖拽上传 + 进度 | `a-upload`(`draggable`) |
| 已上传文档列表 | `a-list` |
| 来源片段折叠 | `a-collapse` / `a-collapse-item` |
| 提问输入框 + 发送 | `a-input` / `a-textarea` + `a-button` |
| 加载态 | `a-spin` |
| 空状态 | `a-empty` |
| 错误/成功提示 | `a-message`(`Message.error/success`) |

## 上传页

`a-upload` 拖拽上传,绑定 `@progress` 显示进度;成功后刷新 `a-list` 文档列表(从后端拉 `documents`)。上传中/失败用 `a-message` 反馈。

## 聊天页(流式)

- 用 `fetch` + `ReadableStream`(或 SSE / `EventSource`)接后端流式答案,**逐块 append 到当前 AI 消息**,实现打字机效果。
- 用户消息靠右、AI 消息靠左的气泡布局;发送时禁用按钮 + `a-spin`,流结束恢复。
- 维护本地消息列表 `messages: {role, content, sources}[]`,流式更新最后一条 AI 消息的 content。

## 来源展示(核心卖点)

每条 AI 回答**下方**放一个可展开的 `a-collapse`,标题 "📎 来源";展开后列出后端随答案返回的命中片段(显示文档名 + 页码/片段序号 + 片段文本)。**后端返回了 sources 就一定要渲染出来**,这是产品最值钱的专业感来源。

## 打磨基线

loading(`a-spin`)、空状态(`a-empty`,如还没上传文档时)、错误提示(`a-message`)三态齐全即可。界面**干净专业**就行,不求花哨,别过度设计。

## 不要做

- 不做移动端适配、不做多用户/权限 UI(MVP 之外)。
- 不引入 Element Plus / Tailwind 等其他 UI 体系,统一用 Arco。
