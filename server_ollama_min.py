@echo off
setlocal enableextensions
title Lanzador Arkaios
cd /d "%~dp0"
chcp 65001 >nul

echo [1/3] Iniciando Ollama...
start "" "C:\Users\djklm\AppData\Local\Programs\Ollama\ollama.exe" serve

echo [2/3] Iniciando servidor Arkaios (minimo)...
REM *** OJO: usa el python embebido en /resources de tu app ***
if not exist "%cd%\resources\python.exe" (
  echo ERROR: No se encontro "%cd%\resources\python.exe"
  pause
  exit /b 1
)
if not exist "C:\arkaios\ui_local\server_ollama_min.py" (
  echo ERROR: No se encontro C:\arkaios\ui_local\server_ollama_min.py
  pause
  exit /b 1
)
start "" "%cd%\resources\python.exe" C:\arkaios\ui_local\server_ollama_min.py

echo [3/3] Abriendo ArkaiosApp...
start "" "%cd%\ArkaiosApp.exe"

echo Listo. Cierra esta ventana si ya no la necesitas.
exit /b
