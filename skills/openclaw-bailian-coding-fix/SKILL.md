---
name: openclaw-bailian-coding-fix
description: Fix OpenClaw code-export 401 issues for Bailian Coding Plan by switching to coding.dashscope endpoint, clearing agent model cache, restarting gateway, and verifying with direct/API tests.
---

# OpenClaw Bailian Coding Fix

Use this skill when `code-export` (or another profile) returns `HTTP 401: Incorrect API key provided` while using Bailian models.

## When to use

- User says Bailian key works in console but OpenClaw still fails.
- OpenClaw returns 401 for `bailian/*` models.
- There may be stale cache in `agents/main/agent/models.json`.

## Key finding from this incident

A common failure mode is config/cache mismatch:

- `openclaw.json` has `models.providers.bailian.baseUrl = https://coding.dashscope.aliyuncs.com/v1`
- but `agents/main/agent/models.json` still keeps old `https://dashscope.aliyuncs.com/compatible-mode/v1`

OpenClaw can keep using cached provider settings and keep failing with 401 until cache is cleared.

## Required endpoint for Coding Plan keys

Use:

`https://coding.dashscope.aliyuncs.com/v1`

Not:

`https://dashscope.aliyuncs.com/compatible-mode/v1`

## Workflow

1. Confirm active profile and target model.
2. Set Bailian base URL to `https://coding.dashscope.aliyuncs.com/v1`.
3. Set default model to `bailian/qwen3-coder-plus` (or user target model).
4. Clear stale cache file: `~/.openclaw-<profile>/agents/main/agent/models.json`.
5. Restart `openclaw-gateway-<profile>.service`.
6. Verify with:
- direct HTTP test (`curl`) to coding endpoint
- OpenClaw agent call

## Scripts

- `scripts/fix-code-export.sh`
  - one-shot fix + verify
- `scripts/test-direct.sh`
  - direct endpoint test using current config

## Quick run

```bash
bash /root/.codex/skills/openclaw-bailian-coding-fix/scripts/fix-code-export.sh \
  --profile code-export \
  --provider bailian \
  --base-url https://coding.dashscope.aliyuncs.com/v1 \
  --model qwen3-coder-plus \
  --api-key '<YOUR_KEY>'
```

If key is already configured, omit `--api-key`.
