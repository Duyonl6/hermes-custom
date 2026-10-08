#!/usr/bin/env bash
# Chạy Tiệm nhà Cam trên macOS/Linux: ./run.sh  → http://localhost:8010
set -e
cd "$(dirname "$0")"
PY=$(command -v python3 || command -v python) || { echo "Chưa cài Python 3.10+"; exit 1; }
[ -x .venv/bin/python ] || "$PY" -m venv .venv
.venv/bin/python -m pip install -q --disable-pip-version-check -r requirements.txt
echo "Đang chạy: http://localhost:${PORT:-8010}  (Ctrl+C để tắt)"
exec .venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port "${PORT:-8010}"
