---
description: 从 task.md 找下一个待办任务并实现它
---

读取 [task.md](../../task.md),按阶段顺序找到**第一个状态为 ⬜ 的任务**(跳过标了 ⏸️ 等待中的项,如域名相关的 4.0 / 4.5)。

然后:
1. 用一句话说明你要做哪个任务(编号 + 标题)。
2. 进入 RIPER 的 PLAN 模式:对照 [plan.md](../../plan.md) 和 [CLAUDE.md](../../CLAUDE.md) 的开发规则,给出该任务的实施清单。
3. 等我回复 `EXECUTE` 后再动手实现。
4. 实现并自测通过后,把 task.md 里该任务前的 ⬜ 改成 ✅,并把状态进行中的临时标记清理掉。

务必遵守 CLAUDE.md 的开发规则(AI 走 ai_client、答案带来源、SQLite、Arco、守 MVP 边界等)。

如有参数 `$ARGUMENTS`,则优先实现指定编号的任务(例如 `/next-task 1.3`)。
