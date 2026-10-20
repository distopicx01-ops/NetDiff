#!/usr/bin/env bash
set -e

TARGET="${1:-127.0.0.1}"

if [ -f ".venv/bin/python" ]; then
    PYTHON_BIN=".venv/bin/python"
elif [ -f ".venv/Scripts/python.exe" ]; then
    PYTHON_BIN=".venv/Scripts/python.exe"
else
    PYTHON_BIN="python"
fi

$PYTHON_BIN -m CLI.cli scan "$TARGET"
