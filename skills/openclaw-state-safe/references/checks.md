# OpenClaw Checks

Use these checks as a live-state checklist.

## Version and update

```bash
openclaw --version
npm view openclaw version
pnpm ls -g --depth 0
```

## Services

```bash
systemctl --user is-active openclaw-gateway.service
systemctl --user is-active openclaw-gateway-code-export.service
systemctl --user status openclaw-gateway.service --no-pager -n 40
systemctl --user status openclaw-gateway-code-export.service --no-pager -n 40
journalctl --user -u openclaw-gateway.service -n 80 --no-pager
journalctl --user -u openclaw-gateway-code-export.service -n 80 --no-pager
```

## Channels and bots

```bash
openclaw channels status --probe
openclaw --profile code-export channels status --probe
openclaw health
openclaw --profile code-export health
```

Interpretation:
- `configured` means credentials/config exist.
- `running` means provider started.
- `connected` means live socket/login is up.
- `works` means probe succeeded.
- `config-only` means the gateway or provider was not fully reachable during the probe.

## Config and profiles

```bash
openclaw config get channels --json
openclaw --profile code-export config get channels --json
openclaw config get agents.defaults.model --json
openclaw --profile code-export config get agents.defaults.model --json
rg -n 'channel|telegram|discord|feishu|model|provider|thinking' ~/.openclaw/openclaw.json ~/.openclaw-code-export/openclaw.json
```

## Cron isolation

```bash
openclaw cron list --json
find ~/.openclaw/cron -maxdepth 2 -type f
sed -n '1,220p' ~/.openclaw/cron/jobs.json
```

Use cron checks when logs show model or auth failures that do not match the current channel or profile state.
