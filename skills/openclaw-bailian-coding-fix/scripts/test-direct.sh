#!/usr/bin/env bash
set -euo pipefail

PROFILE="code-export"
PROVIDER="bailian"
CONFIG=""
MODEL_OVERRIDE=""
BASE_URL_OVERRIDE=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --profile) PROFILE="$2"; shift 2 ;;
    --provider) PROVIDER="$2"; shift 2 ;;
    --config) CONFIG="$2"; shift 2 ;;
    --model) MODEL_OVERRIDE="$2"; shift 2 ;;
    --base-url) BASE_URL_OVERRIDE="$2"; shift 2 ;;
    *) echo "Unknown arg: $1" >&2; exit 2 ;;
  esac
done

if ! command -v jq >/dev/null 2>&1; then echo "jq not found" >&2; exit 1; fi
if ! command -v curl >/dev/null 2>&1; then echo "curl not found" >&2; exit 1; fi

if [[ -z "$CONFIG" ]]; then
  if [[ "$PROFILE" == "default" ]]; then
    CONFIG="/root/.openclaw/openclaw.json"
  else
    CONFIG="/root/.openclaw-${PROFILE}/openclaw.json"
  fi
fi

[[ -f "$CONFIG" ]] || { echo "config not found: $CONFIG" >&2; exit 1; }

BASE_URL="${BASE_URL_OVERRIDE:-$(jq -r --arg p "$PROVIDER" '.models.providers[$p].baseUrl // empty' "$CONFIG")}"
API_KEY="$(jq -r --arg p "$PROVIDER" '.models.providers[$p].apiKey // empty' "$CONFIG")"
PRIMARY="$(jq -r '.agents.defaults.model.primary // empty' "$CONFIG")"

if [[ -n "$MODEL_OVERRIDE" ]]; then
  MODEL_ID="$MODEL_OVERRIDE"
else
  MODEL_ID="${PRIMARY#*/}"
fi

[[ -n "$BASE_URL" ]] || { echo "missing baseUrl" >&2; exit 1; }
[[ -n "$API_KEY" ]] || { echo "missing apiKey" >&2; exit 1; }
[[ -n "$MODEL_ID" ]] || { echo "missing model" >&2; exit 1; }

[[ "$BASE_URL" == */ ]] && BASE_URL="${BASE_URL%/}"
ENDPOINT="$BASE_URL/chat/completions"

TMP_HDR="$(mktemp)"
TMP_BODY="$(mktemp)"
trap 'rm -f "$TMP_HDR" "$TMP_BODY"' EXIT

PAYLOAD="$(jq -nc --arg m "$MODEL_ID" '{model:$m,messages:[{role:"user",content:"Reply with OK only."}],temperature:0}')"
HTTP_CODE="$(curl -sS -o "$TMP_BODY" -D "$TMP_HDR" -w '%{http_code}' \
  -X POST "$ENDPOINT" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $API_KEY" \
  -d "$PAYLOAD")"

echo "profile=$PROFILE"
echo "provider=$PROVIDER"
echo "base_url=$BASE_URL"
echo "model=$MODEL_ID"
echo "http_code=$HTTP_CODE"
echo "--- response headers ---"
sed -n '1,20p' "$TMP_HDR"
echo "--- response body ---"
cat "$TMP_BODY"
