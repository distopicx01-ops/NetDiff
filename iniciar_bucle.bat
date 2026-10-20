@echo off
title NetDiff - Bucle de Monitoreo
cd /d "%~dp0"

echo ===================================================
echo             INICIANDO NETDIFF EN BUCLE             
echo ===================================================
echo.

if exist .venv\Scripts\python.exe (
    set PYTHON_EXEC=.venv\Scripts\python.exe
) else (
    set PYTHON_EXEC=python
)

%PYTHON_EXEC% modo_dual.py %*

pause
