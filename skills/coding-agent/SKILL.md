# coding-agent - OpenClaw Gateway Skill

运行 Codex CLI、Claude Code、OpenCode 或 Pi Coding Agent，通过后台进程进行程序化控制。

## 概述

`coding-agent` 是一个 OpenClaw Skills 集成，用于编写工作流。通过 `exec/process` 后台会话运行各种 AI 编程工具，支持程序化控制、会话追踪和进程管理。

## 前置要求

### OpenClaw Gateway 必需（跨平台）

默认环境已安装 OpenClaw Gateway（`openclaw` CLI）。`process action:*` 的会话管理能力由 Gateway 提供。

### 依赖工具

至少需要安装以下工具之一：
- `codex` - Codex CLI
- `claude` - Claude Code
- `opencode` - OpenCode
- `pi` - Pi Coding Agent

---

## 核心概念

### 工作目录 (workdir)

使用 `workdir` 参数让 AI 只看到相关目录的文件，避免它读取无关文件而"跑偏"。

```bash
# 在目标目录启动 Agent
bash workdir:~/project background:true command:"codex exec --full-auto 'Build a snake game'"

# 或者使用临时目录进行独立任务
SCRATCH=$(mktemp -d)
bash workdir:$SCRATCH background:true command:"codex exec --full-auto 'Your task'"
```

### 后台模式 vs tmux 模式

| 模式 | 适用场景 | 命令 |
|------|----------|------|
| **bash background** | 非交互式、一次性任务 | `bash background:true` |
| **tmux** | 长时间交互任务、需要 TTY | `tmux new-session` |

---

## 使用模式

### 基础使用流程

```bash
# 1. 在后台启动 Agent
bash workdir:~/project background:true command:"codex exec --full-auto 'Your prompt'"
# 返回 sessionId 用于追踪

# 2. 监控进度
process action:log sessionId:XXX

# 3. 检查是否完成
process action:poll sessionId:XXX

# 4. 发送输入（如果 Agent 提问）
process action:write sessionId:XXX data:"y"

# 5. 终止任务（如需）
process action:kill sessionId:XXX

# 6. 列出所有会话
process action:list
```

---

## Codex CLI 使用指南

### 基本命令

```bash
# --full-auto: 沙箱模式，自动批准工作区更改
bash workdir:~/project background:true command:"codex exec --full-auto 'Build a snake game with dark theme'"

# --yolo: 无沙箱，无批准（最快，最危险）
bash workdir:~/project background:true command:"codex --yolo 'Build a snake game with dark theme'"
```

### 审查 PR

⚠️ **重要:** 永远不要在 Clawdbot 自己项目的文件夹里审查 PR！

```bash
# 方式 1: 在实际项目审查（如果是其他项目）
bash workdir:~/Projects/some-other-repo background:true command:"codex review --base main"

# 方式 2: 克隆到临时文件夹安全审查（Clawdbot 的 PR 必须用这个）
REVIEW_DIR=$(mktemp -d)
git clone https://github.com/clawdbot/clawdbot.git $REVIEW_DIR
cd $REVIEW_DIR && gh pr checkout 130
bash workdir:$REVIEW_DIR background:true command:"codex review --base origin/main"

# 方式 3: 使用 git worktree
git worktree add /tmp/pr-130-review pr-130-branch
bash workdir:/tmp/pr-130-review background:true command:"codex review --base main"
```

### 批量审查 PR（并行）

```bash
# 先获取所有 PR refs
git fetch origin '+refs/pull/*/head:refs/remotes/origin/pr/*'

# 部署多个 Codex 并行审查
bash workdir:~/project background:true command:"codex exec 'Review PR #86. git diff origin/main...origin/pr/86'"
bash workdir:~/project background:true command:"codex exec 'Review PR #87. git diff origin/main...origin/pr/87'"
bash workdir:~/project background:true command:"codex exec 'Review PR #95. git diff origin/main...origin/pr/95'"

# 监控所有任务
process action:list

# 获取结果并发布到 GitHub
process action:log sessionId:XXX
gh pr comment <PR#> --body "<review content>"
```

---

## Claude Code 使用

```bash
bash workdir:~/project background:true command:"claude 'Your task'"
```

---

## OpenCode 使用

```bash
bash workdir:~/project background:true command:"opencode run 'Your task'"
```

---

## Pi Coding Agent 使用

### 安装
```bash
npm install -g @mariozechner/pi-coding-agent
```

### 基本使用

```bash
bash workdir:~/project background:true command:"pi 'Your task'"
```

### 常用参数

- `--api-key <key>`: 覆盖 API key（默认使用环境变量）
- `--model <model>`: 选择模型（默认: gemini-2.5-flash）
- `--provider <provider>`: 选择供应商（默认: google）
- `--print` / `-p`: 非交互模式，运行提示后退出

```bash
# 设置供应商 + 模型，非交互模式
bash workdir:~/project background:true command:"pi --provider openai --model gpt-4o-mini -p 'Summarize src/'"
```

---

## tmux 交互模式

对于长时间交互任务，使用 tmux 模式：

```bash
# 创建 tmux 会话
tmux new-session -d -s codex-session "codex exec --full-auto 'Your task'"

# 查看进度
tmux capture-pane -p -t codex-session -S -30

# 发送输入
tmux send-keys -t codex-session "y" Enter

# 检查是否完成
tmux capture-pane -p -t codex-session -S -3 | grep -q "❯" && echo "Done!"

# 终止会话
tmux kill-session -t codex-session
```

---

## 并行修复多个 Issue

结合 git worktrees + tmux 并行修复多个问题：

```bash
# 1. 克隆仓库到临时位置
cd /tmp && git clone git@github.com:user/repo.git repo-worktrees
cd repo-worktrees

# 2. 为每个 Issue 创建 worktree（隔离分支！）
git worktree add -b fix/issue-78 /tmp/issue-78 main
git worktree add -b fix/issue-99 /tmp/issue-99 main

# 3. 设置 tmux 会话
SOCKET="${TMPDIR:-/tmp}/codex-fixes.sock"
tmux -S "$SOCKET" new-session -d -s fix-78
tmux -S "$SOCKET" new-session -d -s fix-99

# 4. 在每个会话中启动 Codex
tmux -S "$SOCKET" send-keys -t fix-78 "cd /tmp/issue-78 && pnpm install && codex --yolo 'Fix issue #78: <description>. Commit and push.'" Enter
tmux -S "$SOCKET" send-keys -t fix-99 "cd /tmp/issue-99 && pnpm install && codex --yolo 'Fix issue #99: <description>. Commit and push.'" Enter

# 5. 监控进度
tmux -S "$SOCKET" capture-pane -p -t fix-78 -S -30
tmux -S "$SOCKET" capture-pane -p -t fix-99 -S -30

# 6. 检查是否完成
tmux -S "$SOCKET" capture-pane -p -t fix-78 -S -3 | grep -q "❯" && echo "Done!"

# 7. 创建 PR
cd /tmp/issue-78 && git push -u origin fix/issue-78
gh pr create --repo user/repo --head fix/issue-78 --title "fix: ..." --body "..."

# 8. 清理
tmux -S "$SOCKET" kill-server
git worktree remove /tmp/issue-78
git worktree remove /tmp/issue-99
```

**为什么用 worktrees?** 每个 Codex 在独立分支工作，不会冲突，可以同时运行 5+ 个并行修复。

---

## 重要规则

1. **永远不要在 `~/Projects/clawdbot/` 里 checkout 分支** — 那是线上 Clawdbot 实例！
2. **永远不要在 `~/clawd/` 里启动** — AI 会读取你的个人文档！
3. **并行是可以的** — 可以同时运行多个 Codex 进程处理批量任务
4. **用 `--full-auto` 构建** — 自动批准更改
5. **用 `process:log` 监控** — 检查进度，不要干涉
6. **保持耐心** — 不要因为 AI "慢"就杀死会话
7. **尊重工具选择** — 如果用户要求用 Codex，就必须用 Codex，不要自己动手！

---

## PR 模板（推荐格式）

提交 PR 时使用此格式：

```markdown
## 原始需求
[确切的要求/问题陈述]

## 实现内容
[高层描述]

**功能:**
- [核心功能 1]
- [核心功能 2]

**示例用法:**
```bash
# 示例
command example
```

## 功能意图
[为什么有用，适合什么工作流]

## 提示词历史（带时间戳）
- YYYY-MM-DD HH:MM UTC: [步骤 1]
- YYYY-MM-DD HH:MM UTC: [步骤 2]

## 测试方法
**手动验证:**
1. [测试步骤] - 输出: [结果]
2. [测试步骤] - 结果: [结果]

**测试的文件:**
- [详情]
- [边界情况]

## 会话日志（实现）
- [研究了什么是]
- [发现了什么是]
- [花费时间]

## 实现细节
**新文件:**
- `path/file.ts` - [描述]

**修改的文件:**
- `path/file.ts` - [更改]

**技术说明:**
- [详情 1]
- [详情 2]
```

---

## 权限与安全

安全级别 L1：低风险技能，只需最少权限。生产环境使用前请审查输入输出。
