#!/usr/bin/env bash
set -euo pipefail

PROFILE="${1:-code-export}"
STATE_DIR="/root/.openclaw-${PROFILE}"
SERVICE="openclaw-gateway-${PROFILE}.service"
if [[ "$PROFILE" == "default" ]]; then
  STATE_DIR="/root/.openclaw"
  SERVICE="openclaw-gateway.service"
fi

CONFIG="${STATE_DIR}/openclaw.json"
COMMANDS_LOG="${STATE_DIR}/logs/commands.log"
CACHE="${STATE_DIR}/agents/main/agent/models.json"

if [[ ! -f "$CONFIG" ]]; then
  echo "config_not_found=$CONFIG" >&2
  exit 1
fi

echo "profile=$PROFILE"
echo "state_dir=$STATE_DIR"
echo "service=$SERVICE"
echo "service_active=$(systemctl --user is-active "$SERVICE" 2>/dev/null || true)"
echo "default_model=$(jq -r '.agents.defaults.model.primary // empty' "$CONFIG")"
echo "telegram_channel_enabled=$(jq -r '.channels.telegram.enabled // empty' "$CONFIG")"
echo "telegram_account_keys=$(jq -r '.channels.telegram.accounts | keys | join(",")' "$CONFIG" 2>/dev/null || true)"
echo "cache_exists=$([[ -f "$CACHE" ]] && echo yes || echo no)"

if [[ -f "$COMMANDS_LOG" ]]; then
  echo "recent_commands:"
  tail -n 5 "$COMMANDS_LOG"
fi

echo "recent_service_log:"
journalctl --user -u "$SERVICE" -n 30 --no-pager | rg -n "401|authentication_error|getUpdates conflict|not authorized|starting provider|agent model|listening on ws" || true

if [[ "$PROFILE" != "default" && -f /root/.openclaw/openclaw.json ]]; then
  THIS_TOKEN="$(jq -r '.channels.telegram.accounts[]?.botToken // empty' "$CONFIG" | head -n 1)"
  DEFAULT_TOKEN="$(jq -r '.channels.telegram.accounts[]?.botToken // empty' /root/.openclaw/openclaw.json | head -n 1)"
  if [[ -n "$THIS_TOKEN" && -n "$DEFAULT_TOKEN" ]]; then
    if [[ "$THIS_TOKEN" == "$DEFAULT_TOKEN" ]]; then
      echo "telegram_token_overlap=yes"
    else
      echo "telegram_token_overlap=no"
    fi
  fi
fi
