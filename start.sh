#!/usr/bin/env bash
set -e
cd "$(dirname "${BASH_SOURCE[0]}")"

if [ -x ".venv/bin/python" ]; then
    PY=".venv/bin/python"
elif [ -x ".venv/Scripts/python.exe" ]; then
    PY=".venv/Scripts/python.exe"
else
    PY="python"
fi

case "$1" in
    docker) docker compose up -d --build ;;
    daemon) "$PY" -m backend.daemon ;;
    api)    "$PY" -m uvicorn backend.api:app --host 0.0.0.0 --port 8000 ;;
    test)   "$PY" -m unittest discover -s tests -t . ;;
    "")     "$PY" modo_dual.py ;;
    *)      "$PY" modo_dual.py "$@" ;;
esac
