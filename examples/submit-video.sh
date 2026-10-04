#!/usr/bin/env bash
set -euo pipefail
: "${ARGOLINK_API_KEY:?set ARGOLINK_API_KEY first}"
BASE="${ARGOLINK_BASE_URL:-https://api.argolink.io}"
REQUEST_ID=$(curl -fsS "$BASE/v1/videos/generations" \
  -H "Authorization: Bearer $ARGOLINK_API_KEY" -H 'Content-Type: application/json' \
  -d '{"model":"seedance-2.5","prompt":"A slow product reveal in soft morning light","duration":6,"resolution":"720p","aspect_ratio":"16:9"}' | jq -er '.request_id')
echo "request_id=$REQUEST_ID"
