---
description: 把本地提交推送到 GitHub 远程仓库
---

把当前分支的提交推送到 GitHub。流程:

1. **推送前检查**:并行运行 `git status`、`git log origin/<当前分支>..HEAD --oneline`(看有哪些待推送的提交)、`git remote -v`(确认远程存在)。命令按全局约定加 `rtk` 前缀。
2. **若有未提交改动**:提示我——是先用 `/commit` 提交,还是只推送已有提交。不要擅自把工作区改动一起推上去。
3. **没有远程时**:若 `git remote` 为空(仓库还没连 GitHub),提示我先建远程,并给出命令示例(`gh repo create` 或 `git remote add origin <url>`),等我确认后再执行。
4. **首次推送某分支**:用 `git push -u origin <当前分支>` 建立上游跟踪;之后用 `git push`。
5. **安全提醒**:
   - 推送前再确认这是公开作品集仓库,**没有把密钥/`.env`/数据文件**推上去。
   - 默认分支(main/master)直推前先问我一句确认。
6. **收尾**:推送成功后,若是 GitHub 仓库,给出仓库/分支的可点击链接。

注意:GitHub 操作优先用 `gh` CLI;git 命令用 `rtk git ...`。`$ARGUMENTS` 可指定分支或附加参数(如 `--force-with-lease`,慎用并先和我确认)。
