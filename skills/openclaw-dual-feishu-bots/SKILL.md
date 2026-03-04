---
name: openclaw-dual-feishu-bots
description: Create and operate two fully isolated Feishu bots in OpenClaw using separate profiles, state dirs, workspaces, ports, and gateway services.
---

# OpenClaw Dual Feishu Bots

## Overview

Use this skill when the user wants two Feishu bots that do not share memory, persona, session history, or workspace files.

This skill implements a hard-isolation architecture: one OpenClaw profile per bot.

## When To Use

- User asks for "两个独立 bot", "防串台", "memory 独立", or similar.
- Current setup has multiple Feishu accounts under one `channels.feishu.accounts` and they are sharing one workspace.
- User wants stable operation across reboots with systemd services.

## Target Architecture

- Profile A: `~/.openclaw` (example bot: `default`)
- Profile B: `~/.openclaw-<name>` (example bot: `code-export`)
- Independent for each profile:
  - `openclaw.json`
  - `agents.defaults.workspace`
  - session store
  - memory files
  - gateway port
  - systemd service

## Workflow

1. Backup current config.
2. Keep profile A with only bot A account.
3. Create profile B directory and copy config.
4. In profile B, keep only bot B account and set:
   - independent workspace path
   - independent gateway port
   - independent gateway token
5. Start/enable profile B gateway as a separate systemd unit.
6. Verify:
   - both ports are listening
   - both profiles health check OK
   - message send succeeds from both bots to their own targets

## Commands (Reference Pattern)

```bash
# 0) Backup
cp ~/.openclaw/openclaw.json ~/.openclaw/openclaw.json.bak.$(date +%Y%m%d%H%M%S)

# 1) Create second profile dir
mkdir -p ~/.openclaw-code-export
cp ~/.openclaw/openclaw.json ~/.openclaw-code-export/openclaw.json

# 2) Default profile: keep only default bot account
jq '.channels.feishu.accounts={"default": .channels.feishu.accounts.default}' \
  ~/.openclaw/openclaw.json > ~/.openclaw/openclaw.json.tmp && \
  mv ~/.openclaw/openclaw.json.tmp ~/.openclaw/openclaw.json

# 3) code-export profile: keep only code-export account + isolated workspace/port/token
NEW_TOKEN=$(openssl rand -hex 24)
jq --arg token "$NEW_TOKEN" '
  .agents.defaults.workspace=(env.HOME + "/.openclaw-code-export/workspace") |
  .gateway.port=18790 |
  .gateway.auth.mode="token" |
  .gateway.auth.token=$token |
  .channels.feishu.accounts={"code-export": .channels.feishu.accounts["code-export"]}
' ~/.openclaw-code-export/openclaw.json > ~/.openclaw-code-export/openclaw.json.tmp && \
mv ~/.openclaw-code-export/openclaw.json.tmp ~/.openclaw-code-export/openclaw.json
```

## Systemd Service For Second Profile

Create `~/.config/systemd/user/openclaw-gateway-code-export.service` and include:

- `ExecStart` pointing to OpenClaw with `--profile code-export gateway --port 18790`
- `Environment=OPENCLAW_STATE_DIR=...`
- `Environment=OPENCLAW_CONFIG_PATH=...`

Then:

```bash
systemctl --user daemon-reload
systemctl --user enable --now openclaw-gateway-code-export.service
```

## Validation Checklist

- `openclaw channels list --json` shows only bot A account.
- `openclaw --profile code-export channels list --json` shows only bot B account.
- `ss -lntp | rg ':18789|:18790'` shows both listeners.
- `openclaw health` and `openclaw --profile code-export health` both show `Feishu: ok`.
- Send one message through each profile and capture both `messageId`.

## Safety Notes

- Never delete user data directories during migration.
- Never expose secrets in chat output.
- If any config becomes inconsistent, restore from the backup and re-apply steps.
