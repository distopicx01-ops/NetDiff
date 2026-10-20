@echo off
title NetDiff
cd /d "%~dp0"

if exist .venv\Scripts\python.exe (
    set PYTHON_EXEC=.venv\Scripts\python.exe
) else (
    set PYTHON_EXEC=python
)

%PYTHON_EXEC% modo_dual.py %*
pause
