#!/usr/bin/env bash
set -e
cd "$(dirname "${BASH_SOURCE[0]}")/.."

if [ $# -lt 1 ]; then
    echo "Uso: scripts/scan.sh <red>   ejemplo: scripts/scan.sh 192.168.1.0/24"
    exit 1
fi

if [ -x ".venv/bin/python" ]; then
    PY=".venv/bin/python"
elif [ -x ".venv/Scripts/python.exe" ]; then
    PY=".venv/Scripts/python.exe"
else
    PY="python"
fi

"$PY" -m CLI.cli scan "$1"
