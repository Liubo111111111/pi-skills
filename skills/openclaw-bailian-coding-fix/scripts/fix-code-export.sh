#!/usr/bin/env bash
set -euo pipefail

PROFILE="code-export"
PROVIDER="bailian"
BASE_URL="https://coding.dashscope.aliyuncs.com/v1"
MODEL="qwen3-coder-plus"
API_KEY=""
RESTART_SERVICE=1
RUN_DIRECT_TEST=1
RUN_AGENT_TEST=1

while [[ $# -gt 0 ]]; do
  case "$1" in
    --profile) PROFILE="$2"; shift 2 ;;
    --provider) PROVIDER="$2"; shift 2 ;;
    --base-url) BASE_URL="$2"; shift 2 ;;
    --model) MODEL="$2"; shift 2 ;;
    --api-key) API_KEY="$2"; shift 2 ;;
    --no-restart) RESTART_SERVICE=0; shift ;;
    --no-direct-test) RUN_DIRECT_TEST=0; shift ;;
    --no-agent-test) RUN_AGENT_TEST=0; shift ;;
    *) echo "Unknown arg: $1" >&2; exit 2 ;;
  esac
done

if ! command -v openclaw >/dev/null 2>&1; then echo "openclaw not found" >&2; exit 1; fi
if ! command -v jq >/dev/null 2>&1; then echo "jq not found" >&2; exit 1; fi

STATE_DIR="/root/.openclaw-${PROFILE}"
if [[ "$PROFILE" == "default" ]]; then
  STATE_DIR="/root/.openclaw"
fi
CONFIG_PATH="$STATE_DIR/openclaw.json"
CACHE_PATH="$STATE_DIR/agents/main/agent/models.json"
SERVICE_NAME="openclaw-gateway-${PROFILE}.service"
if [[ "$PROFILE" == "default" ]]; then
  SERVICE_NAME="openclaw-gateway.service"
fi

[[ -f "$CONFIG_PATH" ]] || { echo "config not found: $CONFIG_PATH" >&2; exit 1; }

echo "[1/6] Configure provider baseUrl"
openclaw --profile "$PROFILE" config set "models.providers.${PROVIDER}.baseUrl" "$BASE_URL"

echo "[2/6] Ensure default model"
openclaw --profile "$PROFILE" models set "${PROVIDER}/${MODEL}"

if [[ -n "$API_KEY" ]]; then
  echo "[3/6] Update API key"
  openclaw --profile "$PROFILE" config set "models.providers.${PROVIDER}.apiKey" "$API_KEY"
else
  echo "[3/6] Skip API key update (using existing key in config)"
fi

echo "[4/6] Clear stale agent model cache"
if [[ -f "$CACHE_PATH" ]]; then
  cp "$CACHE_PATH" "${CACHE_PATH}.bak.$(date +%Y%m%d%H%M%S)"
  rm -f "$CACHE_PATH"
  echo "cache removed: $CACHE_PATH"
else
  echo "cache not found, skip"
fi

if [[ $RESTART_SERVICE -eq 1 ]]; then
  echo "[5/6] Restart gateway service: $SERVICE_NAME"
  systemctl --user restart "$SERVICE_NAME"
  systemctl --user is-active "$SERVICE_NAME"
else
  echo "[5/6] Skip restart"
fi

echo "[6/6] Verify"
if [[ $RUN_DIRECT_TEST -eq 1 ]]; then
  bash /root/.codex/skills/openclaw-bailian-coding-fix/scripts/test-direct.sh \
    --profile "$PROFILE" --provider "$PROVIDER" --model "$MODEL" --base-url "$BASE_URL"
fi

if [[ $RUN_AGENT_TEST -eq 1 ]]; then
  openclaw --profile "$PROFILE" agent --agent main --message "Reply with OK only." --json
fi
