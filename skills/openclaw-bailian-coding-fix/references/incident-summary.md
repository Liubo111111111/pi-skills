# Incident Summary: OpenClaw code-export Bailian 401

## Symptom

`openclaw --profile code-export agent ...` returned:

- `HTTP 401: Incorrect API key provided`

## What was confirmed

1. Direct call to `https://dashscope.aliyuncs.com/compatible-mode/v1` with the same key returned 401.
2. Direct call to `https://coding.dashscope.aliyuncs.com/v1` with the same key returned 200.
3. `openclaw.json` was switched to coding endpoint, but OpenClaw still returned 401.
4. Root cause found: stale cache at `~/.openclaw-code-export/agents/main/agent/models.json` still pointed to old compatible-mode endpoint.
5. After deleting cache and restarting gateway, OpenClaw call succeeded.

## Root cause

OpenClaw agent-side model cache retained old provider endpoint and overrode effective runtime behavior.

## Permanent fix pattern

1. Use coding endpoint for Coding Plan key:
   - `https://coding.dashscope.aliyuncs.com/v1`
2. Keep provider/model on `bailian/qwen3-coder-plus` (or desired model).
3. Remove stale cache file:
   - `~/.openclaw-<profile>/agents/main/agent/models.json`
4. Restart gateway service:
   - `systemctl --user restart openclaw-gateway-<profile>.service`
5. Verify both:
   - direct curl test
   - OpenClaw agent test
