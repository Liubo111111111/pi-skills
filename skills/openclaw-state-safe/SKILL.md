---
name: openclaw-state-safe
description: Accurate inspection and low-risk maintenance for an existing OpenClaw deployment. Use when the user asks which model, version, profile, channel, bot, service, or config is currently active; whether OpenClaw or installed skills need updating; whether Feishu, Discord, Telegram, or other channels are healthy; whether a config value already exists; or asks to change profiles, channels, gateway services, or related systemd units. Verify live state with CLI, config files, and service logs before answering or editing.
---

# OpenClaw State Safe

Use this skill to answer OpenClaw operational questions from live state instead of memory. The main goal is to prevent false answers about current model, installed skills, config presence, update status, and channel health.

## Workflow

1. Identify the target scope first.
- Decide whether the user means the default profile, a named profile such as `code-export`, or all profiles.
- If the request is ambiguous but low-risk, inspect both default and named profiles before answering.

2. Verify before replying.
- For version or update questions, check the installed version and the current upstream/package version from live sources.
- For model, channel, and bot questions, use `openclaw health` or `openclaw channels status --probe`, then confirm with recent service logs if the service is restarting.
- For config existence, use `openclaw config get` or inspect the actual config file. Never answer "already exists" without reading the value.
- For installed skills, inspect the real skill directories or skill commands. Do not infer from prior turns or stale summaries.

3. Separate facts from interpretations.
- Distinguish `configured`, `running`, `connected`, and `works`.
- If a command runs during a gateway restart window, treat a temporary `1006` or `config-only` result as inconclusive until service logs confirm the final state.
- Treat stale-socket restarts as self-healing unless they repeat continuously.

4. Edit the smallest surface that fixes the problem.
- When changing channels or providers, modify only the affected profile.
- Keep profile isolation intact: separate config, service, workspace, and ports.
- The account key `default` is acceptable in multiple profiles because the isolation boundary is the profile, not the key name.

5. Be careful around upgrades.
- Validate config compatibility before updating OpenClaw.
- After upgrading, ensure systemd services do not point to stale version-pinned package paths.
- Prefer stable executable entrypoints when possible, then restart all affected services and re-check channels.

6. Do not mix unrelated failures into one diagnosis.
- Channel health issues, plugin API mismatch, config validation errors, and cron/model failures are different classes of problems.
- If logs show a bad cron job using a dead model, report it separately from channel health.

## Frequent Failure Modes

- Outdated config keys after an OpenClaw upgrade.
- Services pinned to an old `.pnpm/openclaw@...` path.
- Plugin API mismatch from an old extension.
- False answers about the active model or installed skills because nothing was checked live.
- Transient restart windows misread as permanent failure.

## Response Rules

- Put findings first: version, services, channels, config validity, then side issues.
- Use exact profile names and dates when clarifying time-sensitive state.
- Say explicitly when something is an inference from logs rather than a direct command result.
- If the user asks for a change, perform the change, restart the affected service, and verify the result in the same turn.

## Reference

Read [checks.md](references/checks.md) for the command checklist to use for version checks, channel health, config validation, service diagnosis, and cron isolation.
