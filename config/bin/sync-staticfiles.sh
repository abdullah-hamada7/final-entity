#!/usr/bin/env bash
# Copy source static assets into STATIC_ROOT for production (WhiteNoise).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cp -a "$ROOT/static/css/." "$ROOT/staticfiles/css/"
echo "Synced static/css -> staticfiles/css"
