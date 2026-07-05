#!/usr/bin/env bash
# Copy source static assets into STATIC_ROOT for production (WhiteNoise).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cp -a "$ROOT/static/css/." "$ROOT/staticfiles/css/"
cp -a "$ROOT/static/js/." "$ROOT/staticfiles/js/"
if [ -f "$ROOT/static/site.webmanifest" ]; then
  cp -a "$ROOT/static/site.webmanifest" "$ROOT/staticfiles/site.webmanifest"
fi
echo "Synced static assets -> staticfiles/"
