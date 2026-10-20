#!/usr/bin/env bash
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

if [ -f ".venv/bin/python" ]; then
    PYTHON_BIN=".venv/bin/python"
elif [ -f ".venv/Scripts/python.exe" ]; then
    PYTHON_BIN=".venv/Scripts/python.exe"
else
    PYTHON_BIN="python"
fi

case "$1" in
    --docker)
        echo "Iniciando con Docker Compose..."
        docker compose up -d --build
        ;;
    --daemon)
        echo "Iniciando solo demonio en bucle..."
        $PYTHON_BIN -m backend.daemon
        ;;
    --api)
        echo "Iniciando solo API..."
        $PYTHON_BIN -m uvicorn backend.api:app --host 0.0.0.0 --port 8000 --reload
        ;;
    *)
        echo "Iniciando Modo Dual (Local)..."
        $PYTHON_BIN modo_dual.py "$@"
        ;;
esac
