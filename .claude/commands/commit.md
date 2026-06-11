---
description: 检查改动、生成规范的提交信息并提交代码
---

为当前改动生成一次规范的 Git 提交。流程:

1. **看清改动**:并行运行 `git status`、`git diff`(已暂存 + 未暂存)、`git log --oneline -5`(参考本仓库已有的提交风格)。命令按全局约定加 `rtk` 前缀。
2. **安全检查(必做)**:
   - 确认**没有**把密钥/敏感文件纳入提交——尤其 `.env`、Chroma 数据目录、上传文件目录、SQLite 数据文件。若发现已被追踪,**先停下提醒我**,别提交。
   - 若仓库还没有 `.gitignore` 或漏了上述条目,先提示补上。
3. **暂存**:`git add` 相关文件(默认 `git add -A`;若 `$ARGUMENTS` 指定了路径,只加这些)。
4. **写提交信息**:遵循 Conventional Commits,标题用英文、祈使句、≤72 字符:
   - 类型:`feat` / `fix` / `docs` / `refactor` / `chore` / `test` / `style` / `build`
   - 格式:`<type>(<scope>): <subject>`,scope 用 `backend` / `frontend` / `deploy` / `docs` 等
   - 例:`feat(backend): add document ingest pipeline with chunking`
   - 改动跨多个关注点时,正文用要点列出;否则只要标题。
   - 若 `$ARGUMENTS` 提供了说明文字,以它为提交主旨。
5. **提交**:用 HEREDOC 提交以保证格式正确,信息末尾附:
   ```
   Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>
   ```
6. **收尾**:`git status` 确认提交成功。**不要 `git push`**,除非我明确要求。

注意:本机已装 RTK,所有 git 命令用 `rtk git ...`。若当前在默认分支(main/master)上且这是功能性改动,先提示我是否需要新建分支再提交。
