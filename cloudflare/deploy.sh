#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="$(mktemp -d)"
cp "$ROOT"/*.html "$ROOT"/gh.png "$ROOT"/caixa.png "$ROOT"/ijh.jpg "$OUT"/ 2>/dev/null || true
cp "$ROOT"/cloudflare/_worker.js "$OUT"/_worker.js
wrangler pages deploy "$OUT" --project-name mercadolivre-taxa-pix --commit-dirty=true
