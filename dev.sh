#!/usr/bin/env bash
# Runs the backend and frontend together. Ctrl+C stops both.
cd "$(dirname "$0")"
trap 'kill 0' EXIT
(cd backend && uv run uvicorn app.main:app --reload --port 8000) &
(cd frontend && npm run dev) &
wait
