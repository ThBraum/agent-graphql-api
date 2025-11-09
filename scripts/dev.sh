#!/usr/bin/env bash
set -euo pipefail
export PYTHONUNBUFFERED=1
cp -n .env.example .env 2>/dev/null || true
poetry run uvicorn app.main:app --reload --port 8000
