---
name: openclaw-no-reply-fix
description: Diagnose and fix OpenClaw bots that receive messages but do not reply, covering model 401 errors, Telegram polling conflicts, and Telegram authorization policy mistakes.
---

# OpenClaw No Reply Fix

Use this skill when an OpenClaw bot "does not reply", replies intermittently, or returns Telegram authorization errors while the gateway appears to be running.

## When To Use

- The bot receives messages but nothing is sent back.
- `commands.log` shows incoming commands but no visible response reaches Telegram or Feishu.
- `openclaw --profile <name> agent ...` fails while direct model calls still work.
- Telegram logs show `409 Conflict` for `getUpdates`.
- Telegram replies with `You are not authorized to use this command.`

## Common Root Causes

1. Model/provider mismatch:
   - The profile default model points to the wrong provider.
   - Example from this incident: `code-export` used `minimax-portal/MiniMax-M2.5` and returned `HTTP 401 authentication_error`.
2. Duplicate Telegram polling:
   - Two OpenClaw profiles use the same Telegram bot token.
   - Both gateways poll `getUpdates`, causing repeated `409 Conflict`.
3. Telegram access policy too strict:
   - `dmPolicy=pairing` blocks direct messages from users who are not paired.
   - Switching to `dmPolicy=open` also requires `allowFrom=["*"]`.

## Workflow

1. Confirm which profile and channel are affected.
2. Check whether messages are entering OpenClaw:
   - `~/.openclaw[-<profile>]/logs/commands.log`
3. Test the model directly and through the agent:
   - direct provider HTTP call
   - `openclaw --profile <profile> agent --agent main --message ... --json`
4. If the agent fails with `401`, inspect:
   - `agents.defaults.model.primary`
   - provider base URL
   - cached `agents/main/agent/models.json`
5. For Telegram bots, verify token isolation:
   - compare bot tokens across profiles
   - confirm each token maps to a different bot via `getMe`
6. If Telegram returns authorization errors, inspect:
   - `channels.telegram.accounts.<account>.dmPolicy`
   - `channels.telegram.accounts.<account>.groupPolicy`
   - `channels.telegram.accounts.<account>.allowFrom`
7. Restart the affected gateway and verify with:
   - `systemctl --user is-active ...`
   - recent `journalctl --user -u ...`
   - one more `openclaw --profile ... agent` test

## Fast Checks

- Incoming command seen:
  - `sed -n '1,120p' ~/.openclaw-<profile>/logs/commands.log`
- Active model:
  - `openclaw --profile <profile> config get agents.defaults.model.primary`
- Telegram bot identity:
  - `curl https://api.telegram.org/bot<TOKEN>/getMe`
- Gateway logs:
  - `journalctl --user -u openclaw-gateway-<profile>.service -n 80 --no-pager`

## Fix Patterns

### A. Agent returns provider 401

- Point the profile back to the intended provider/model.
- If using Bailian Coding Plan, use `https://coding.dashscope.aliyuncs.com/v1`.
- Clear `~/.openclaw-<profile>/agents/main/agent/models.json`.
- Restart the profile gateway.

If this is specifically a Bailian Coding Plan issue, also use `openclaw-bailian-coding-fix`.

### B. Telegram `409 Conflict`

- Compare bot tokens across profiles.
- If two profiles share one token, split them so each profile has its own bot.
- Restart both gateways after the token/config change.
- Re-check logs; new `409 Conflict` lines should stop appearing.

### C. Telegram `You are not authorized to use this command`

For a bot that should accept direct messages openly, set:

```json
{
  "dmPolicy": "open",
  "groupPolicy": "open",
  "allowFrom": ["*"]
}
```

Important:

- `dmPolicy=open` without `allowFrom=["*"]` fails config validation.
- Account-level settings under `channels.telegram.accounts.<account>` are the safest place to change this.

## Script

- `scripts/diagnose-no-reply.sh`
  - Collects the current model, gateway status, recent logs, and Telegram token overlap signal for `default` and one extra profile.

## Verification Standard

A fix is complete only when all of the following are true:

- direct provider call succeeds
- `openclaw --profile <profile> agent ... --json` returns `status=ok`
- gateway service is `active`
- no fresh Telegram `409 Conflict` lines appear after restart
- the bot responds to a real user message
