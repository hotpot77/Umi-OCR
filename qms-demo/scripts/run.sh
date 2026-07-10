#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"
if [[ ! -d .venv ]]; then
  python3 -m venv .venv
  .venv/bin/pip install -U pip
  .venv/bin/pip install -r requirements.txt
fi
export PYTHONPATH="$ROOT/backend"
exec .venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8088 --reload
