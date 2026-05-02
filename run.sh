#!/usr/bin/env bash
set -euo pipefail

export PYTHONPATH=src

if [[ ! -d ".venv" ]]; then
  python3 -m venv .venv
fi

source .venv/bin/activate
pip install -r requirements.txt
exec .venv/bin/uvicorn asimov.api:app --host "${ASIMOV_HOST:-0.0.0.0}" --port "${ASIMOV_PORT:-8000}"
